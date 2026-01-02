"""
歌曲信息数据模型

包含歌曲的基本信息，如歌曲ID、名称、歌手、专辑、风格标签等
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class SongInfo:
    """歌曲信息模型

    用于存储从网易云音乐API获取的歌曲基本信息

    Attributes:
        song_id: 网易云歌曲ID
        name: 歌曲名称
        artist: 歌手名称
        album: 专辑名称
        genres: 音乐风格标签列表（从songTag字段获取）
        duration: 时长（秒）
    """
    song_id: str
    name: str
    artist: str
    album: str = ""
    genres: List[str] = field(default_factory=list)
    duration: int = 0

    def get_genres_str(self) -> str:
        """获取风格字符串（最多显示3个标签）

        Returns:
            str: 用 " / " 分隔的风格标签字符串，如果没有标签则返回 "未知风格"
        """
        if not self.genres:
            return "未知风格"

        # 最多显示3个标签
        display_genres = self.genres[:3]
        return " / ".join(display_genres)

    def __str__(self) -> str:
        """字符串表示

        Returns:
            str: 格式为 "歌曲名 - 歌手名" 的字符串
        """
        return f"{self.name} - {self.artist}"
