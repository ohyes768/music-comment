"""
评论展示组件

显示歌曲信息和评论轮播
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QCursor, QFont

from src.config.settings import get_config
from src.utils.logger import get_logger
from src.models.song_info import SongInfo
from src.models.comment import Comment

logger = get_logger()


class CommentWidget(QWidget):
    """评论展示组件

    显示歌曲信息和评论轮播，支持淡入淡出动画
    """

    # 定义信号：评论更新时发出，用于通知主窗口调整高度
    comment_updated = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        """初始化评论展示组件

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.config = get_config()

        # 数据
        self.current_song: SongInfo = None
        self.comments: list[Comment] = []
        self.current_index: int = 0

        # 定时器
        self.timer: QTimer = None

        # UI组件
        self.song_label: QLabel = None
        self.comment_label: QLabel = None
        self.counter_label: QLabel = None
        self.meta_label: QLabel = None
        self.likes_label: QLabel = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置UI组件 - 紧凑设计"""
        layout = QVBoxLayout()
        # 紧凑边距：上下16px，左右16px
        layout.setContentsMargins(16, 16, 16, 16)
        # 间距缩小
        layout.setSpacing(0)

        # 标题（歌曲名）：16px，白色，加粗（缩小字体）
        self.song_label = QLabel()
        self.song_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 700;
                background-color: transparent;
                padding: 0px;
            }
        """)
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.song_label)

        # 添加12px间距
        layout.addSpacing(12)

        # 评论内容：14px，白色（缩小字体）
        self.comment_label = QLabel()
        self.comment_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 400;
                background-color: transparent;
                padding: 0px;
                line-height: 1.4;
            }
        """)
        self.comment_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.comment_label.setWordWrap(True)
        # 不设置最大高度，允许根据内容动态调整
        layout.addWidget(self.comment_label)

        # 添加弹性空间，把用户名和点赞数推到底部
        layout.addStretch()

        # 互动区：计数器和用户名（底部）
        from PyQt6.QtWidgets import QHBoxLayout
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)

        # 计数器标签：12px，白色，左下角
        self.counter_label = QLabel()
        self.counter_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 400;
                background-color: transparent;
                padding: 0px;
            }
        """)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        h_layout.addWidget(self.counter_label)

        # 添加弹簧，推用户名到右边
        h_layout.addStretch()

        # 用户名：12px，白色（改为白色，缩小字体）
        self.meta_label = QLabel()
        self.meta_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 400;
                background-color: transparent;
                padding: 0px;
            }
        """)
        h_layout.addWidget(self.meta_label)

        # 点赞数：12px，白色（缩小字体）
        from PyQt6.QtWidgets import QLabel as QLabel2
        self.likes_label = QLabel2()
        self.likes_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 400;
                background-color: transparent;
                padding: 0px;
            }
        """)
        h_layout.addWidget(self.likes_label)

        layout.addLayout(h_layout)

        self.setLayout(layout)

    def update_song(
        self,
        song: SongInfo,
        comments: list[Comment]
    ) -> None:
        """更新歌曲和评论

        Args:
            song: 歌曲信息
            comments: 评论列表
        """
        self.current_song = song
        self.comments = comments
        self.current_index = 0

        # 更新歌曲信息
        self._update_song_info()

        # 更新评论
        self._update_comment()

        # 启动轮播
        self._start_rotation()

        logger.debug(
            f"更新歌曲: {song.name} - {song.artist}, "
            f"评论数: {len(comments)}"
        )

    def _update_song_info(self) -> None:
        """更新歌曲信息显示"""
        if not self.current_song:
            return

        # 歌曲名（不加emoji）
        self.song_label.setText(f"{self.current_song.name} - {self.current_song.artist}")

    def _update_comment(self) -> None:
        """更新评论显示"""
        if not self.comments or self.current_index >= len(self.comments):
            self.comment_label.setText("暂无评论")
            self.counter_label.setText("0/0")
            self.meta_label.setText("")
            if hasattr(self, 'likes_label'):
                self.likes_label.setText("")
            # 发出信号，通知窗口调整高度
            self.comment_updated.emit()
            return

        comment = self.comments[self.current_index]

        # 评论内容（不加引号）
        self.comment_label.setText(comment.content)

        # 计数器显示：当前索引+1/总评论数
        self.counter_label.setText(f"{self.current_index + 1}/{len(self.comments)}")

        # 用户名和点赞数在右下角显示
        self.meta_label.setText(f"{comment.user} · {comment.get_likes_str()}")

        if hasattr(self, 'likes_label'):
            self.likes_label.setText("")  # 不再单独显示点赞数

        # 发出信号，通知窗口调整高度
        self.comment_updated.emit()

    def _start_rotation(self) -> None:
        """开始评论轮播"""
        # 停止旧定时器
        if self.timer:
            self.timer.stop()

        # 创建新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._next_comment)
        self.timer.start(self.config.rotation_interval)

        logger.debug(f"启动评论轮播，间隔: {self.config.rotation_interval}ms")

    def _next_comment(self) -> None:
        """切换到下一条评论"""
        if not self.comments:
            return

        self.current_index = (self.current_index + 1) % len(self.comments)
        self._update_comment()

        logger.debug(f"切换到第 {self.current_index + 1} 条评论")

    def stop_rotation(self) -> None:
        """停止评论轮播"""
        if self.timer:
            self.timer.stop()
            logger.debug("停止评论轮播")
