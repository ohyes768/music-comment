"""
主窗口模块

创建透明悬浮的主窗口，包含评论展示组件
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMenu, QMessageBox, QSystemTrayIcon, QApplication
from PyQt6.QtCore import Qt, QPoint, QSize, QEvent, QObject, QTimer
from PyQt6.QtGui import QCursor, QIcon, QPainter, QColor, QBrush, QAction, QImage, QPixmap
import keyboard

from src.config.settings import get_config
from src.utils.logger import get_logger
from src.gui.comment_widget import CommentWidget

logger = get_logger()


def create_tray_icon() -> QIcon:
    """创建系统托盘图标

    绘制一个简单的音符图标

    Returns:
        QIcon: 托盘图标
    """
    # 创建 32x32 的图像
    size = 32
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))  # 透明背景

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绘制音符形状（八分音符）
    # 符头（椭圆）
    painter.setBrush(QBrush(QColor(230, 50, 50)))  # 红色
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(8, 20, 10, 8)

    # 符干（竖线）
    painter.setBrush(QBrush(QColor(230, 50, 50)))
    painter.drawRect(17, 4, 2, 16)

    # 符尾（曲线）
    from PyQt6.QtGui import QPainterPath
    path = QPainterPath()
    path.moveTo(19, 4)
    path.quadTo(24, 8, 24, 14)
    path.quadTo(24, 18, 19, 12)
    painter.setBrush(QBrush(QColor(230, 50, 50)))
    painter.drawPath(path)

    painter.end()

    # 从 QImage 创建 QPixmap，再创建 QIcon
    pixmap = QPixmap.fromImage(image)
    return QIcon(pixmap)


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

        # 系统托盘
        self.tray_icon: QSystemTrayIcon = None

        self._setup_window()
        self._setup_ui()
        self._setup_tray()  # 设置系统托盘
        self._setup_global_hotkey()  # 设置全局快捷键

    def _setup_window(self) -> None:
        """配置窗口属性"""
        # 窗口标志 - 去掉 Tool 属性，让窗口能在任务栏显示
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # 无边框
            Qt.WindowType.WindowStaysOnTopHint |     # 置顶
            Qt.WindowType.WindowMinimizeButtonHint  # 显示最小化按钮
        )

        # 背景透明（支持半透明效果）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 窗口大小（初始大小）
        self.resize(self.config.window_width, self.config.window_height)

        # 设置窗口尺寸策略：宽度固定，高度根据内容调整
        from PyQt6.QtWidgets import QSizePolicy
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Fixed,      # 宽度固定
            QSizePolicy.Policy.Preferred   # 高度根据内容
        )
        self.setSizePolicy(size_policy)
        self.background_container = None  # 先初始化，后面会在 _setup_ui 中创建

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

        # 设置容器尺寸：宽度固定，高度根据内容调整
        self.background_container.setMinimumWidth(self.config.window_width)
        self.background_container.setMaximumWidth(self.config.window_width)

        # 容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 创建评论展示组件
        self.comment_widget = CommentWidget(self.background_container)
        # 连接评论更新信号到窗口高度调整槽
        self.comment_widget.comment_updated.connect(self._adjust_window_height)
        container_layout.addWidget(self.comment_widget)

        self.background_container.setLayout(container_layout)
        layout.addWidget(self.background_container)

        self.setLayout(layout)

        # 设置主窗口的宽度约束，高度允许动态调整
        self.setMinimumWidth(self.config.window_width)
        self.setMaximumWidth(self.config.window_width)
        self.setMinimumHeight(100)  # 最小高度
        # 不设置最大高度，允许根据内容动态调整

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

    def _setup_tray(self) -> None:
        """设置系统托盘"""
        # 创建托盘图标
        icon = create_tray_icon()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)

        # 创建托盘菜单
        tray_menu = QMenu()

        # 显示/隐藏窗口
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self._show_window)
        tray_menu.addAction(show_action)

        hide_action = QAction("隐藏到托盘", self)
        hide_action.triggered.connect(self._hide_to_tray)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)

        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self._on_tray_activated)

        # 显示托盘图标
        self.tray_icon.show()

        # 设置提示文本
        self.tray_icon.setToolTip("网易云音乐评论 - 摸鱼神器")

        logger.info("系统托盘初始化完成")

    def _setup_global_hotkey(self) -> None:
        """设置全局快捷键"""
        try:
            # 注册 Ctrl+Alt+; 快捷键来切换窗口显示/隐藏
            keyboard.add_hotkey('ctrl+alt+;', self._toggle_window)
            logger.info("全局快捷键已注册: Ctrl+Alt+; (切换窗口显示/隐藏)")
        except Exception as e:
            logger.error(f"注册全局快捷键失败: {e}")

    def _show_window(self) -> None:
        """显示窗口"""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _hide_to_tray(self) -> None:
        """隐藏到托盘"""
        self.hide()

    def _toggle_window(self) -> None:
        """切换窗口显示/隐藏（全局快捷键回调）"""
        # 使用 QTimer 将操作调度到主线程（keyboard 回调在独立线程）
        QTimer.singleShot(0, self._toggle_window_impl)

    def _toggle_window_impl(self) -> None:
        """切换窗口显示/隐藏的实际实现（在主线程执行）"""
        if self.isVisible():
            self._hide_to_tray()
            logger.debug("快捷键触发: 隐藏窗口")
        else:
            self._show_window()
            logger.debug("快捷键触发: 显示窗口")

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """托盘图标激活事件

        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击托盘图标显示窗口
            if self.isVisible():
                self.hide()
            else:
                self._show_window()

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

        双击隐藏到托盘/显示窗口

        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isVisible():
                self._hide_to_tray()
            else:
                self._show_window()
            event.accept()

    def contextMenuEvent(self, event) -> None:
        """右键菜单事件

        显示右键菜单，包含最小化、最大化、退出等选项

        Args:
            event: 上下文菜单事件
        """
        menu = QMenu(self)

        # 最小化/还原（右键菜单）
        if self.isVisible():
            minimize_action = menu.addAction("隐藏到托盘")
            minimize_action.triggered.connect(self._hide_to_tray)
        else:
            show_action = menu.addAction("显示窗口")
            show_action.triggered.connect(self._show_window)

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
                # 最小化时隐藏到托盘（不占任务栏）
                self.hide()
                logger.debug("窗口已隐藏到托盘")

        super().changeEvent(event)

    def update_song(self, song_info, comments: list) -> None:
        """更新歌曲和评论

        Args:
            song_info: 歌曲信息
            comments: 评论列表
        """
        self.comment_widget.update_song(song_info, comments)

        # 更新后调整窗口高度以适应内容
        self._adjust_window_height()

    def _adjust_window_height(self) -> None:
        """根据内容调整窗口高度，保持窗口位置不变"""
        # 保存当前窗口位置
        current_pos = self.pos()

        # 强制布局更新
        self.background_container.layout().activate()
        self.comment_widget.layout().activate()

        # 获取内容需要的实际高度
        content_height = self.background_container.sizeHint().height()

        # 确保高度在合理范围内（最小100，最大600）
        new_height = max(100, min(content_height, 600))

        # 调整窗口大小
        self.resize(self.config.window_width, new_height)

        # 恢复窗口位置，确保不会移动
        self.move(current_pos)

    def closeEvent(self, event) -> None:
        """窗口关闭事件

        清理快捷键注册

        Args:
            event: 关闭事件
        """
        try:
            # 移除所有快捷键
            keyboard.unhook_all_hotkeys()
            logger.info("全局快捷键已注销")
        except Exception as e:
            logger.error(f"注销快捷键失败: {e}")

        # 接受关闭事件
        event.accept()
