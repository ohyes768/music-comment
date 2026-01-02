"""
评论数据模型

包含网易云音乐评论的信息，如评论内容、用户、点赞数等
"""

from dataclasses import dataclass


@dataclass
class Comment:
    """评论信息模型

    用于存储从网易云音乐API获取的热门评论信息

    Attributes:
        content: 评论内容
        user: 用户昵称
        likes: 点赞数
        time: 评论时间戳（字符串格式）
    """
    content: str
    user: str
    likes: int
    time: str = ""

    def get_likes_str(self) -> str:
        """获取格式化的点赞数字符串

        Returns:
            str: 格式化后的点赞数，如 "1.2k"、"342" 等
        """
        if self.likes >= 1000:
            return f"{self.likes / 1000:.1f}k"
        return str(self.likes)

    def __str__(self) -> str:
        """字符串表示（仅显示评论内容的前30个字符）

        Returns:
            str: 评论内容的简短表示
        """
        content_preview = self.content[:30]
        if len(self.content) > 30:
            content_preview += "..."
        return f"{self.user}: {content_preview}"
