"""
网易云音乐爬虫客户端

直接调用网易云 Web API，无需第三方 API 服务
"""

import time
from typing import Optional, List
from functools import lru_cache
from datetime import datetime

import requests

from src.config.settings import get_config
from src.utils.logger import get_logger
from src.models.song_info import SongInfo
from src.models.comment import Comment
from src.core.crypto import NeteaseCrypto

logger = get_logger()


class NeteaseMusicCrawler:
    """网易云音乐爬虫客户端

    直接调用网易云 Web API 接口，不依赖第三方 API 服务
    MVP版本：使用无需加密的接口
    """

    BASE_URL = "https://music.163.com/api"

    def __init__(self):
        """初始化爬虫客户端"""
        config = get_config()
        self.timeout = config.api_timeout
        self.max_retries = config.max_retries
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_interval = 1.0  # 最小请求间隔（秒）

    def _rate_limit(self) -> None:
        """请求频率限制"""
        now = time.time()
        elapsed = now - self.last_request_time

        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_request_time = time.time()

    def _safe_request(
        self,
        url: str,
        params: dict,
        method: str = "GET"
    ) -> Optional[dict]:
        """安全的API请求（带重试）

        Args:
            url: 请求URL
            params: 请求参数
            method: 请求方法（GET/POST）

        Returns:
            Optional[dict]: API响应的JSON数据，失败则返回 None
        """
        self._rate_limit()

        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.session.get(
                        url,
                        params=params,
                        timeout=self.timeout
                    )
                else:
                    response = self.session.post(
                        url,
                        data=params,
                        timeout=self.timeout
                    )

                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                logger.warning(
                    f"API请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    # 指数退避
                    sleep_time = 2 ** attempt
                    time.sleep(sleep_time)
                else:
                    logger.error(f"API请求失败，已达最大重试次数")
                    return None

        return None

    def search_song(
        self,
        song_name: str,
        artist_name: str
    ) -> Optional[str]:
        """搜索歌曲，返回song_id

        Args:
            song_name: 歌曲名称
            artist_name: 歌手名称

        Returns:
            Optional[str]: 找到的歌曲ID，未找到则返回 None
        """
        keywords = f"{song_name} {artist_name}"
        url = f"{self.BASE_URL}/search/get/web"
        params = {
            "s": keywords,
            "type": "1",  # 1=单曲
            "offset": "0",
            "limit": "5"
        }

        logger.info(f"搜索歌曲: {keywords}")
        response = self._safe_request(url, params)

        if not response or response.get("code") != 200:
            logger.error("搜索歌曲失败")
            return None

        songs = response.get("result", {}).get("songs", [])
        if not songs:
            logger.warning(f"未找到歌曲: {keywords}")
            return None

        # 返回第一个结果的ID
        song_id = str(songs[0]["id"])
        logger.info(f"找到歌曲ID: {song_id}")
        return song_id

    @lru_cache(maxsize=50)
    def get_song_detail(self, song_id: str) -> Optional[SongInfo]:
        """获取歌曲详情（带缓存）

        注意：MVP版本无法获取歌曲风格标签
        评论接口需要加密参数，暂不可用

        Args:
            song_id: 歌曲ID

        Returns:
            Optional[SongInfo]: 歌曲详情对象，失败则返回 None
        """
        url = f"{self.BASE_URL}/song/detail"
        params = {"ids": f'["{song_id}"]'}  # JSON数组格式: ["543965520"]

        logger.debug(f"获取歌曲详情: {song_id}")
        response = self._safe_request(url, params)

        if not response or response.get("code") != 200:
            logger.error(f"获取歌曲详情失败: {song_id}")
            return None

        songs = response.get("songs", [])
        if not songs:
            logger.warning(f"歌曲详情为空: {song_id}")
            return None

        song_data = songs[0]

        # V2版本：使用专辑类型和子类型作为风格标签的替代
        # 网易云 /api/song/detail 接口不返回 songTag 字段
        # 因此我们使用 album.type 和 album.subType 作为风格标签
        album_data = song_data.get("album", {})
        genres = []

        # 添加专辑类型（Single/Album/EP等）
        album_type = album_data.get("type", "")
        if album_type:
            # 翻译专辑类型
            type_map = {
                "Single": "单曲",
                "Album": "专辑",
                "EP": "EP",
                "Single": "单曲"
            }
            type_cn = type_map.get(album_type, album_type)
            genres.append(type_cn)

        # 添加专辑子类型（如"录音室版"、"现场版"等）
        sub_type = album_data.get("subType", "")
        if sub_type and sub_type not in genres:
            genres.append(sub_type)

        # 如果没有任何标签，添加默认值
        if not genres:
            genres = ["流行"]

        return SongInfo(
            song_id=str(song_data.get("id")),
            name=song_data.get("name", ""),
            artist=song_data.get("artists", [{}])[0].get("name", ""),
            album=song_data.get("album", {}).get("name", ""),
            genres=genres,
            duration=song_data.get("duration", 0) // 1000
        )

    @lru_cache(maxsize=50)
    def get_hot_comments(self, song_id: str) -> List[Comment]:
        """获取热门评论（带缓存）

        V2版本：实现了加密算法，可以获取真实评论

        Args:
            song_id: 歌曲ID

        Returns:
            List[Comment]: 热门评论列表
        """
        logger.debug(f"获取热门评论: {song_id}")

        # 评论API地址
        url = "https://music.163.com/weapi/comment/resource/comments/get?csrf_token="

        # 请求参数
        request_data = {
            'csrf_token': '',
            'cursor': '-1',
            'offset': '0',
            'orderType': '1',  # 1=热门评论
            'pageNo': '1',
            'pageSize': '20',
            'rid': f'R_SO_4_{song_id}',
            'threadId': f'R_SO_4_{song_id}'
        }

        # 加密参数
        encrypted_data = NeteaseCrypto.encrypt_request(request_data)

        # 发送POST请求
        try:
            response = self.session.post(
                url,
                data=encrypted_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                logger.error(f"获取评论失败: {result.get('message', 'Unknown error')}")
                return []

            # 解析评论数据
            hot_comments = result.get("data", {}).get("hotComments", [])
            if not hot_comments:
                logger.warning(f"歌曲 {song_id} 没有热门评论")
                return []

            comments = []
            for item in hot_comments[:20]:  # 最多20条
                # 解析时间戳
                timestamp = item.get("time", 0)
                comment_time = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M')

                comment = Comment(
                    content=item.get("content", ""),
                    user=item.get("user", {}).get("nickname", ""),
                    likes=item.get("likedCount", 0),
                    time=comment_time
                )
                comments.append(comment)

            logger.info(f"成功获取 {len(comments)} 条热门评论")
            return comments

        except Exception as e:
            logger.error(f"获取评论时出错: {e}")
            return []

    def clear_cache(self) -> None:
        """清空缓存"""
        self.get_song_detail.cache_clear()
        self.get_hot_comments.cache_clear()
        logger.info("爬虫缓存已清空")
