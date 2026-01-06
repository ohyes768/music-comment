"""
网易云音乐评论桌面应用 - 应用入口

自动识别当前播放歌曲，获取热门评论并以透明悬浮窗口展示
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, qInstallMessageHandler, QtMsgType

from src.gui.main_window import TransparentWindow
from src.core.monitor import NeteaseWindowMonitor
from src.core.netease_crawler import NeteaseMusicCrawler
from src.utils.logger import get_logger, setup_logger

logger = get_logger()


def qt_message_handler(msg_type: QtMsgType, context, message: str):
    """Qt 消息处理器

    过滤掉 Qt 的警告信息，保持控制台输出干净

    Args:
        msg_type: 消息类型
        context: 消息上下文
        message: 消息内容
    """
    # 只处理警告和调试信息
    if msg_type == QtMsgType.QtWarningMsg:
        # 过滤掉 QWindowsWindow::setGeometry 的警告
        if "QWindowsWindow::setGeometry" in message:
            return
        # 过滤掉 Unable to set geometry 的警告
        if "Unable to set geometry" in message:
            return
    elif msg_type == QtMsgType.QtDebugMsg:
        # 过滤掉所有调试信息
        return

    # 其他消息正常输出
    # 使用默认的处理方式
    pass


class MusicCommentApp:
    """应用主类"""

    # 检测间隔（毫秒）
    CHECK_INTERVAL = 3000  # 每3秒检测一次

    def __init__(self):
        """初始化应用"""
        self.app = QApplication(sys.argv)
        self.window = TransparentWindow()
        self.monitor = NeteaseWindowMonitor()
        self.crawler = NeteaseMusicCrawler()

        # 当前歌曲信息（用于检测变化）
        self.current_song_name = ""
        self.current_artist_name = ""

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_update)
        self.timer.setInterval(self.CHECK_INTERVAL)

    def check_netease_running(self) -> bool:
        """检查网易云音乐是否运行

        Returns:
            bool: 网易云是否正在运行
        """
        try:
            song = self.monitor.get_current_song()
            return song is not None
        except PermissionError as e:
            # 权限错误，重新抛出让上层处理
            raise
        except Exception as e:
            logger.error(f"检查网易云音乐状态时出错: {e}")
            return False

    def fetch_song_data(self, song_name: str, artist_name: str):
        """获取歌曲数据

        Args:
            song_name: 歌曲名称
            artist_name: 歌手名称
        """
        try:
            # 1. 搜索获取 song_id
            song_id = self.crawler.search_song(song_name, artist_name)
            if not song_id:
                logger.warning(f"未找到歌曲: {song_name} - {artist_name}")
                return

            # 2. 获取歌曲详情
            song_detail = self.crawler.get_song_detail(song_id)
            if not song_detail:
                logger.warning(f"获取歌曲详情失败: {song_id}")
                return

            # 3. 获取热门评论
            comments = self.crawler.get_hot_comments(song_id)
            if not comments:
                logger.warning(f"获取评论失败: {song_id}")
                return

            # 4. 更新UI
            self.window.update_song(song_detail, comments)

        except Exception as e:
            logger.error(f"获取歌曲数据时出错: {e}")

    def check_and_update(self):
        """定时检测歌曲变化并更新

        每3秒检测一次当前播放的歌曲，如果发生变化则重新获取数据
        """
        try:
            # 获取当前歌曲
            song = self.monitor.get_current_song()
            if not song:
                return

            # 检查歌曲是否发生变化
            if (song.name != self.current_song_name or
                song.artist != self.current_artist_name):

                logger.info(f"检测到歌曲切换: {self.current_song_name} - {self.current_artist_name} "
                           f"-> {song.name} - {song.artist}")

                # 更新当前歌曲信息
                self.current_song_name = song.name
                self.current_artist_name = song.artist

                # 重新获取数据
                self.fetch_song_data(song.name, song.artist)

        except Exception as e:
            logger.error(f"检测歌曲变化时出错: {e}")

    def run(self) -> int:
        """运行应用

        Returns:
            int: 退出码
        """
        try:
            # 检查网易云音乐是否运行
            if not self.check_netease_running():
                QMessageBox.warning(
                    None,
                    "网易云音乐未运行",
                    "请先启动网易云音乐，然后再运行本应用"
                )
                return 1

            # 获取当前歌曲
            song = self.monitor.get_current_song()
            if song:
                # 保存当前歌曲信息
                self.current_song_name = song.name
                self.current_artist_name = song.artist

                # 获取歌曲数据
                self.fetch_song_data(song.name, song.artist)

            # 显示窗口
            self.window.show()

            # 启动定时器，持续监控歌曲变化
            logger.info(f"启动定时监控，每 {self.CHECK_INTERVAL/1000} 秒检测一次")
            self.timer.start()

            return self.app.exec()

        except PermissionError as e:
            QMessageBox.critical(
                None,
                "权限不足",
                f"需要管理员权限才能运行本程序。\n\n"
                f"请按以下步骤操作：\n"
                f"1. 右键点击 PowerShell 或命令提示符\n"
                f"2. 选择「以管理员身份运行」\n"
                f"3. 再运行本程序\n\n"
                f"错误详情：{e}"
            )
            return 1


def main():
    """主函数"""
    # 安装 Qt 消息处理器，过滤警告信息
    qInstallMessageHandler(qt_message_handler)

    # 设置日志
    setup_logger()

    logger.info("=" * 60)
    logger.info("网易云音乐评论桌面应用启动")
    logger.info("=" * 60)

    try:
        app = MusicCommentApp()
        exit_code = app.run()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
