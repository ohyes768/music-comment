"""
主窗口模块

创建透明悬浮的主窗口，包含评论展示组件
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMenu, QMessageBox
from PyQt6.QtCore import Qt, QPoint, QSize, QEvent, QObject
from PyQt6.QtGui import QCursor, QIcon, QPainter, QColor, QBrush

from src.config.settings import get_config
from src.utils.logger import get_logger
from src.gui.comment_widget import CommentWidget

logger = get_logger()


class BackgroundContainer(QWidget):
    """半透明背景容器

    使用自定义绘制实现真正的半透明背景效果
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 背景颜色：深灰色，60%不透明度
        self.bg_color = QColor(51, 51, 51, 153)  # 153 = 60% of 255

    def paintEvent(self, event):
        """绘制事件 - 绘制半透明背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制圆角矩形背景
        painter.setBrush(QBrush(self.bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)



class TransparentWindow(QWidget):
    """透明悬浮窗口

    无边框、置顶、透明背景的悬浮窗口，用于显示评论
    """

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.config = get_config()
        self.comment_widget: CommentWidget = None

        # 拖动相关
        self._drag_position: QPoint = QPoint()
        self._is_dragging = False

        # 保存窗口状态（用于最小化还原）
        self._saved_geometry = None

        self._setup_window()
        self._setup_ui()

    def _setup_window(self) -> None:
        """配置窗口属性"""
        # 窗口标志 - 添加最小化按钮支持
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # 无边框
            Qt.WindowType.WindowStaysOnTopHint |     # 置顶
            Qt.WindowType.Tool |                    # 工具窗口
            Qt.WindowType.WindowMinimizeButtonHint  # 显示最小化按钮
        )

        # 背景透明（支持半透明效果）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 窗口大小
        self.resize(self.config.window_width, self.config.window_height)

        # 设置鼠标跟踪，以便拖动
        self.setMouseTracking(True)

        logger.info("主窗口初始化完成")

    def _setup_ui(self) -> None:
        """设置UI组件"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建半透明背景容器（使用自定义绘制）
        self.background_container = BackgroundContainer(self)

        # 容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 创建评论展示组件
        self.comment_widget = CommentWidget(self.background_container)
        container_layout.addWidget(self.comment_widget)

        self.background_container.setLayout(container_layout)
        layout.addWidget(self.background_container)

        self.setLayout(layout)

        # 让所有子组件的鼠标事件传递给父窗口
        self.comment_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # 为所有子组件安装事件过滤器，让点击可以拖动窗口
        self._install_event_filter(self)

    def _install_event_filter(self, widget):
        """为组件安装事件过滤器，使其可拖动

        Args:
            widget: 要安装事件过滤器的组件
        """
        # 定义拖动事件过滤器类
        class DragEventFilter(QObject):
            """拖动事件过滤器"""

            def __init__(self, parent_window):
                super().__init__(parent_window)
                self.parent = parent_window

            def eventFilter(self, obj, event):
                # 处理鼠标按下事件（只处理左键，右键留给系统处理菜单）
                if event.type() == QEvent.Type.MouseButtonPress:
                    if event.button() == Qt.MouseButton.LeftButton:
                        # 让父窗口处理拖动
                        self.parent.mousePressEvent(event)
                        return True
                    # 右键不处理，让系统显示菜单

                # 处理鼠标移动事件
                elif event.type() == QEvent.Type.MouseMove:
                    if event.buttons() == Qt.MouseButton.LeftButton:
                        self.parent.mouseMoveEvent(event)
                        return True

                # 处理鼠标释放事件
                elif event.type() == QEvent.Type.MouseButtonRelease:
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.parent.mouseReleaseEvent(event)
                        return True

                # 处理鼠标双击事件
                elif event.type() == QEvent.Type.MouseButtonDblClick:
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.parent.mouseDoubleClickEvent(event)
                        return True

                return False

        # 创建过滤器
        self._drag_filter = DragEventFilter(self)

        # 为当前组件安装事件过滤器
        widget.installEventFilter(self._drag_filter)

        # 递归为所有子组件安装同一个过滤器
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self._drag_filter)

    def mousePressEvent(self, event) -> None:
        """鼠标按下事件

        用于开始拖动窗口

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录拖动起始位置
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件

        用于拖动窗口

        Args:
            event: 鼠标事件
        """
        # 仅在按住左键时拖动
        if event.buttons() == Qt.MouseButton.LeftButton and self._is_dragging:
            # 移动窗口
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        """鼠标双击事件

        双击最小化/还原窗口

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isMinimized():
                self.showNormal()
            else:
                self.showMinimized()
            event.accept()

    def contextMenuEvent(self, event) -> None:
        """右键菜单事件

        显示右键菜单，包含最小化、最大化、退出等选项

        Args:
            event: 上下文菜单事件
        """
        menu = QMenu(self)

        # 最小化/还原
        if self.isMinimized():
            restore_action = menu.addAction("还原")
            restore_action.triggered.connect(self.showNormal)
        else:
            minimize_action = menu.addAction("最小化")
            minimize_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # 退出
        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self.close)

        # 显示菜单
        menu.exec(QCursor.pos())

    def changeEvent(self, event) -> None:
        """窗口状态改变事件

        处理最小化/还原

        Args:
            event: 窗口事件
        """
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                # 最小化时保存窗口位置和大小
                self._saved_geometry = self.geometry()
                logger.info("窗口已最小化")
            else:
                # 还原时恢复窗口位置和大小
                if self._saved_geometry:
                    self.setGeometry(self._saved_geometry)
                    logger.info("窗口已还原")

        super().changeEvent(event)

    def update_song(self, song_info, comments: list) -> None:
        """更新歌曲和评论

        Args:
            song_info: 歌曲信息
            comments: 评论列表
        """
        self.comment_widget.update_song(song_info, comments)
