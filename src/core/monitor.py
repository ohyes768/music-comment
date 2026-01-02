"""
网易云音乐窗口监控模块

负责读取网易云音乐窗口标题，解析出当前播放的歌曲信息
"""

import win32gui
import win32process
import psutil
from typing import Optional, Tuple
from dataclasses import dataclass

from src.utils.logger import get_logger
from src.models.song_info import SongInfo

logger = get_logger()


@dataclass
class WindowInfo:
    """窗口信息数据类"""
    hwnd: int
    title: str
    class_name: str
    pid: int
    is_visible: bool


class NeteaseWindowMonitor:
    """网易云音乐窗口监控器

    通过读取网易云音乐窗口标题来识别当前播放的歌曲
    """

    # 网易云音乐进程名
    PROCESS_NAME = "cloudmusic.exe"

    # 网易云音乐主窗口类名
    WINDOW_CLASS_NAME = "OrpheusBrowserHost"

    def __init__(self):
        """初始化窗口监控器"""
        self.netease_pids: list[int] = []
        self._refresh_netease_pids()

    def _refresh_netease_pids(self) -> None:
        """刷新网易云音乐进程ID列表"""
        self.netease_pids = []

        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and self.PROCESS_NAME in proc.info['name'].lower():
                    self.netease_pids.append(proc.info['pid'])

            if self.netease_pids:
                logger.debug(f"找到网易云音乐进程: {self.netease_pids}")
            else:
                logger.warning("未找到网易云音乐进程")

        except Exception as e:
            logger.error(f"获取进程列表失败: {e}")

    def find_main_window(self) -> Optional[WindowInfo]:
        """查找网易云音乐主窗口

        Returns:
            Optional[WindowInfo]: 找到的窗口信息，如果未找到则返回 None
        """
        # 简化版：直接枚举窗口，不先检查进程ID
        # 这样可以避免 psutil 和 win32process 之间的兼容性问题

        def callback(hwnd, windows):
            """枚举窗口的回调函数"""
            try:
                # 获取窗口类名
                try:
                    class_name = win32gui.GetClassName(hwnd)
                except Exception as e:
                    return True

                # 检查是否是主窗口类名
                if class_name == self.WINDOW_CLASS_NAME:
                    logger.info(f"找到匹配的窗口类名: {class_name} (hwnd={hwnd})")

                    # 获取窗口标题
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        logger.info(f"窗口标题: {title}")
                    except Exception as e:
                        logger.debug(f"获取窗口标题失败 (hwnd={hwnd}): {e}")
                        return True

                    # 检查窗口是否可见
                    try:
                        is_visible = win32gui.IsWindowVisible(hwnd)
                        logger.info(f"窗口可见: {is_visible}")
                    except Exception as e:
                        logger.debug(f"检查窗口可见性失败 (hwnd={hwnd}): {e}")
                        return True

                    # 检查标题是否有效
                    if not title or not is_visible:
                        logger.info(f"窗口被跳过: title={bool(title)}, visible={is_visible}")
                        return True

                    # 获取进程ID（可选）
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    except Exception as e:
                        logger.debug(f"获取窗口进程ID失败 (hwnd={hwnd}): {e}")
                        pid = 0

                    # 找到目标窗口
                    logger.info(f"成功匹配网易云音乐窗口: {title}")
                    window_info = WindowInfo(
                        hwnd=hwnd,
                        title=title,
                        class_name=class_name,
                        pid=pid,
                        is_visible=is_visible
                    )
                    windows.append(window_info)
                    return False  # 停止枚举

                return True

            except Exception as e:
                logger.debug(f"枚举窗口时出错 (hwnd={hwnd}): {e}")
                return True

        windows: list[WindowInfo] = []

        try:
            logger.info("开始枚举所有窗口，查找网易云音乐...")
            win32gui.EnumWindows(callback, windows)
            logger.info(f"枚举完成，找到 {len(windows)} 个网易云音乐窗口")
        except PermissionError as e:
            # 即使 EnumWindows 返回时抛出权限错误，如果已经找到窗口，也继续使用
            if windows:
                logger.warning(f"EnumWindows 返回时出现权限错误，但已找到窗口，继续使用")
            else:
                logger.error(f"权限不足，无法枚举窗口: {e}")
                logger.error("请尝试以管理员身份运行本程序")
                raise PermissionError(
                    "需要管理员权限才能枚举窗口。"
                    "请右键点击 PowerShell 或命令提示符，选择'以管理员身份运行'。"
                ) from e
        except Exception as e:
            # 即使 EnumWindows 返回时抛出其他错误，如果已经找到窗口，也继续使用
            if windows:
                logger.warning(f"EnumWindows 返回时出现错误，但已找到窗口，继续使用: {e}")
            else:
                logger.error(f"枚举窗口时发生未知错误: {e}")
                logger.error(f"错误类型: {type(e).__name__}")
                return None

        if windows:
            logger.info(f"找到网易云音乐主窗口: {windows[0].title}")
            return windows[0]

        logger.warning("未找到网易云音乐主窗口（目标类名: OrpheusBrowserHost）")
        logger.info("调试提示：请确保网易云音乐正在运行且窗口可见")
        return None

    def parse_window_title(self, title: str) -> Optional[Tuple[str, str]]:
        """解析窗口标题

        Args:
            title: 窗口标题，格式为 "歌曲名 - 歌手名"

        Returns:
            Optional[Tuple[str, str]]: 解析出的 (歌曲名, 歌手名)，解析失败则返回 None
        """
        if not title:
            return None

        # 窗口标题格式: "歌曲名 - 歌手名"
        if " - " not in title:
            logger.warning(f"窗口标题格式不正确: {title}")
            return None

        parts = title.split(" - ", 1)
        song_name = parts[0].strip()
        artist_name = parts[1].strip()

        if not song_name or not artist_name:
            logger.warning(f"窗口标题内容为空: {title}")
            return None

        logger.debug(f"解析窗口标题: {title} -> 歌曲: {song_name}, 歌手: {artist_name}")
        return song_name, artist_name

    def get_current_song(self) -> Optional[SongInfo]:
        """获取当前播放的歌曲

        Returns:
            Optional[SongInfo]: 当前歌曲信息，如果未找到则返回 None
        """
        # 1. 查找主窗口
        window_info = self.find_main_window()
        if not window_info:
            return None

        # 2. 解析窗口标题
        result = self.parse_window_title(window_info.title)
        if not result:
            return None

        song_name, artist_name = result

        # 3. 构建 SongInfo 对象（song_id 需要通过 API 搜索获取）
        return SongInfo(
            song_id="",  # 待搜索
            name=song_name,
            artist=artist_name,
            album="",
            genres=[],
            duration=0
        )
