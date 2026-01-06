# 网易云音乐评论桌面应用 - 技术设计文档（TDD）

**文档版本**: v3.0
**创建日期**: 2024-12-30
**最后更新**: 2025-01-06
**文档状态**: 正式发布

---

## 文档信息

| 项目 | 信息 |
|------|------|
| 项目名称 | 网易云音乐评论桌面应用 |
| 技术栈 | Python + PyQt6 |
| 架构模式 | 分层架构（MVC变体） |
| 代码规范 | PEP 8 + Google Style Guide |

---

## 1. 系统架构

### 1.1 整体架构 (V3.0 更新)

V3.0版本新增 **系统托盘功能** 和 **窗口高度自适应机制**。

V2.0版本新增 **crypto模块**，用于实现评论接口加密算法。

```
┌─────────────────────────────────────────────────────────┐
│                     用户界面层 (GUI Layer)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Main Window  │  │Comment Widget│  │Style Manager │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Layer)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Monitor    │  │  API Client  │  │  Song Cache  │  │
│  │              │  │              │  │              │  │
│  │ 窗口标题读取  │  │  搜索/评论   │  │  LRU Cache   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Crypto    │  │Comment Encrypt│  │ Comment Decrypt│  │
│  │   Module    │  │     Manager   │  │     Manager   │  │
│  │   V2.0新增    │  │               │  │               │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     数据层 (Data Layer)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Song Info    │  │   Comment    │  │   Config     │  │
│  │   Model      │  │    Model     │  │   Manager    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Crypto Keys│  │  AES/RSA     │  │  Encryption  │  │
│  │  Storage     │  │  Utilities   │  │  Utils        │  │
│  │   V2.0新增    │  │   V2.0新增    │  │   V2.0新增    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    外部接口层 (External Layer)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Windows API  │  │ Netease API  │  │  File System │  │
│  │ (win32gui)   │  │  (HTTP)      │  │  (Config)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 数据流图 (V2.0 更新)

```
用户启动应用
    ↓
Monitor: 读取窗口标题 → 解析歌曲名+歌手名
    ↓
APIClient: 搜索API → 获取song_id
    ↓
APIClient: 评论API → 获取加密的热门评论
    ↓
Crypto模块: 解密评论内容 → 验证签名
    ↓
APIClient: 详情API → 获取音乐风格
    ↓
Crypto模块: 加密评论用于存储
    ↓
GUI: 显示歌曲信息 + 真实评论轮播
    ↓
用户查看评论（V2.0支持暂停/继续）
```

---

## 2. 模块设计

### 2.1 核心模块概览

| 模块 | 文件 | 功能 | 行数限制 |
|------|------|------|----------|
| 窗口监控 | `monitor.py` | 读取网易云窗口标题 | <300 |
| API客户端 | `api_client.py` | 调用网易云音乐API | <300 |
| 歌曲模型 | `song_info.py` | 歌曲信息数据结构 | <100 |
| 评论模型 | `comment.py` | 评论信息数据结构 | <100 |
| 主窗口 | `main_window.py` | 透明悬浮窗口 | <200 |
| 评论组件 | `comment_widget.py` | 评论轮播组件 | <200 |
| 样式管理 | `style_manager.py` | 界面样式管理 | <100 |
| 配置管理 | `settings.py` | 全局配置管理 | <100 |
| 日志工具 | `logger.py` | 日志记录工具 | <100 |
| **crypto模块** | **crypto/** | **V2.0新增加密算法** | **<300** |
| AES加密器 | `crypto/aes_encryptor.py` | AES加密实现 | <150 |
| AES解密器 | `crypto/aes_decryptor.py` | AES解密实现 | <150 |
| RSA加密器 | `crypto/rsa_encryptor.py` | RSA加密实现 | <150 |
| RSA解密器 | `crypto/rsa_decryptor.py` | RSA解密实现 | <150 |
| 加密管理器 | `crypto/crypto_manager.py` | 统一加密接口 | <200 |
| 密钥存储 | `crypto/key_storage.py` | 加密密钥管理 | <150 |

### 2.2 模块详细设计

#### 2.2.1 窗口监控模块 (monitor.py)

**职责**: 识别当前播放的歌曲

**输入**: 无
**输出**: `SongInfo` 对象

**核心类**:
```python
class NeteaseWindowMonitor:
    """网易云音乐窗口监控器"""

    def find_main_window() -> Optional[dict]:
        """查找网易云主窗口"""
        # 1. 查找 cloudmusic.exe 进程
        # 2. 枚举窗口
        # 3. 查找 OrpheusBrowserHost 类
        # 4. 读取窗口标题
        pass

    def parse_window_title(title: str) -> dict:
        """解析窗口标题"""
        # 格式: "歌曲名 - 歌手名"
        pass

    def get_current_song() -> Optional[SongInfo]:
        """获取当前播放的歌曲"""
        pass
```

**关键流程**:
```
1. 使用 psutil 查找 cloudmusic.exe 进程（可能有多个）
2. 使用 win32gui.EnumWindows 枚举所有窗口
3. 过滤条件：
   - 窗口进程ID = cloudmusic.exe 的PID
   - 窗口类名 = "OrpheusBrowserHost"
   - 窗口可见 = True
   - 窗口标题非空
4. 解析标题: "歌曲名 - 歌手名"
5. 返回 SongInfo(song_name, artist_name)
```

**错误处理**:
- 网易云未运行：返回 None，记录日志
- 窗口未找到：返回 None，记录日志
- 标题格式异常：返回 None，记录日志

---

#### 2.2.2 API客户端模块 (api_client.py)

**职责**: 调用网易云音乐 API，获取评论和详情

**输入**: `song_id` 或搜索关键词
**输出**: 评论列表、歌曲详情

**核心类**:
```python
class NeteaseAPIClient:
    """网易云音乐API客户端"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.cache = LRUCache(maxsize=50)

    def search_song(self, song_name: str, artist_name: str) -> Optional[str]:
        """搜索歌曲，返回 song_id"""
        pass

    def get_hot_comments(self, song_id: str) -> List[Comment]:
        """获取热门评论（前20条）"""
        pass

    def get_song_detail(self, song_id: str) -> SongInfo:
        """获取歌曲详情（包含风格）"""
        pass
```

**API 接口**:
```python
# 搜索歌曲
GET /search?keywords={song_name} {artist_name}
Response: {
    "result": {
        "songs": [
            {"id": 123, "name": "歌名", "artists": [{"name": "歌手"}]}
        ]
    }
}

# 获取热门评论
GET /comment/hot?id={song_id}&limit=20
Response: {
    "hotComments": [
        {"content": "评论内容", "user": {"nickname": "用户"}, "likedCount": 123}
    ]
}

# 获取歌曲详情
GET /song/detail?ids={song_id}
Response: {
    "songs": [
        {"id": 123, "name": "歌名", "alia": ["风格1", "风格2"]}
    ]
}
```

**缓存策略**:
- LRU Cache，最大容量 50
- 评论缓存时间：3600 秒（1小时）
- 歌曲详情缓存时间：86400 秒（24小时）

**错误处理**:
- 请求失败：重试 3 次，指数退避（1s, 2s, 4s）
- API 服务不可用：返回缓存数据（如果有）
- JSON 解析失败：记录日志，返回空列表

---

#### 2.2.3 主窗口模块 (main_window.py)

**职责**: 创建透明悬浮窗口

**核心类**:
```python
class TransparentWindow(QWidget):
    """透明悬浮窗口"""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._setup_mouse_events()

    def _setup_window(self):
        """配置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |      # 无边框
            Qt.WindowType.WindowStaysOnTopHint |     # 置顶
            Qt.WindowType.Tool                        # 工具窗口
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.85)
        self.resize(320, 180)

    def mousePressEvent(self, event):
        """鼠标按下：记录拖动起始位置"""
        pass

    def mouseMoveEvent(self, event):
        """鼠标移动：拖动窗口"""
        pass

    def contextMenuEvent(self, event):
        """右键菜单"""
        pass
```

**窗口属性**:
```python
尺寸: 宽度320px，高度100-600px（动态调整）
无边框: FramelessWindowHint
置顶: WindowStaysOnTopHint
背景透明: WA_TranslucentBackground
整体透明度: 60%（使用 alpha 通道）
可拖动: 自实现鼠标事件
系统托盘: QSystemTrayIcon
```

**V3.0 新增功能**:
- **系统托盘集成**: 使用 QSystemTrayIcon 实现托盘功能
- **窗口高度自适应**: 基于 comment_updated 信号动态调整
- **托盘图标**: 使用 QPainter 手绘红色音符图标
- **托盘交互**: 双击显示/隐藏，右键菜单

**右键菜单**:
```
┌─────────────┐
│ 隐藏到托盘   │
│ 退出        │
└─────────────┘
```

**托盘菜单**:
```
┌─────────────┐
│ 显示窗口     │
│ 隐藏到托盘   │
├─────────────┤
│ 退出        │
└─────────────┘
```

---

#### 2.2.3.1 V3.0 系统托盘模块 (main_window.py)

**职责**: 实现系统托盘功能，让应用最小化后不占任务栏

**核心类**:
```python
def create_tray_icon() -> QIcon:
    """创建系统托盘图标"""
    # 使用 QPainter 手绘红色音符图标
    size = 32
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    # 绘制音符形状...
    pixmap = QPixmap.fromImage(image)
    return QIcon(pixmap)

class TransparentWindow(QWidget):
    def _setup_tray(self) -> None:
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_tray_icon())

        # 托盘菜单
        tray_menu = QMenu()
        show_action = QAction("显示窗口", self)
        hide_action = QAction("隐藏到托盘", self)
        quit_action = QAction("退出", self)

        # 信号连接
        self.tray_icon.activated.connect(self._on_tray_activated)
```

**托盘功能**:
- **图标显示**: 红色音符图标（♪）
- **双击交互**: 双击托盘图标显示/隐藏窗口
- **右键菜单**: 显示窗口、隐藏到托盘、退出
- **提示文本**: "网易云音乐评论 - 摸鱼神器"
- **自动隐藏**: 窗口最小化时自动隐藏到托盘

#### 2.2.3.2 V3.0 窗口高度自适应机制

**职责**: 根据评论内容动态调整窗口高度

**实现原理**:
1. **信号触发**: CommentWidget 发出 comment_updated 信号
2. **布局更新**: 强制激活布局系统
3. **高度计算**: 获取内容的 sizeHint().height()
4. **窗口调整**: 调用 resize() 设置新尺寸

**核心代码**:
```python
class CommentWidget(QWidget):
    comment_updated = pyqtSignal()  # 评论更新信号

    def _update_comment(self) -> None:
        """更新评论显示"""
        # 更新评论内容...
        self.comment_updated.emit()  # 发出信号

class TransparentWindow(QWidget):
    def _adjust_window_height(self) -> None:
        """根据内容调整窗口高度"""
        # 1. 强制布局更新
        self.background_container.layout().activate()
        self.comment_widget.layout().activate()

        # 2. 获取内容需要的实际高度
        content_height = self.background_container.sizeHint().height()

        # 3. 确保高度在合理范围内
        new_height = max(100, min(content_height, 600))

        # 4. 调整窗口大小
        self.resize(self.config.window_width, new_height)
```

**高度范围**:
- 最小高度: 100px（避免窗口过小）
- 最大高度: 600px（避免过度拉伸）
- 宽度固定: 320px

**调整时机**:
- 切换歌曲时
- 评论轮播时
- 任何评论内容更新时

---

#### 2.2.4 评论轮播组件 (comment_widget.py) - V2.0增强

**职责**: 显示歌曲信息和真实评论轮播（支持加密/解密）

**V2.0 新增功能**:
- **真实评论展示**: 显示解密后的真实评论内容
- **轮播控制**: 支持暂停/继续/位置记忆
- **智能间隔**: 根据评论长度自动调整轮播时间
- **动画效果**: 平滑的淡入淡出过渡

**核心类**:
```python
class CommentWidget(QWidget):
    """V2.0 增强版评论展示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_song: SongInfo = None
        self.encrypted_comments: List[dict] = []  # 加密的评论数据
        self.decrypted_comments: List[Comment] = []  # 解密后的评论
        self.current_index: int = 0
        self.timer: QTimer = None
        self.is_paused: bool = False
        self.use_real_comments: bool = True  # V2.0默认显示真实评论
        self.crypto_manager: CryptoManager = None
        self._setup_ui()

    def update_song(self, song: SongInfo, encrypted_comments: List[dict]):
        """V2.0: 更新歌曲和加密评论"""
        self.current_song = song
        self.encrypted_comments = encrypted_comments

        # 异步解密评论
        self.decrypt_comments_async()

        self.current_index = 0
        self._update_display()
        self._start_rotation()

    def decrypt_comments_async(self):
        """异步解密评论内容"""
        # 创建解密线程
        self.decrypt_thread = DecryptThread(
            self.encrypted_comments,
            self.crypto_manager
        )
        self.decrypt_thread.finished.connect(self._on_decrypt_finished)
        self.decrypt_thread.start()

    def toggle_pause(self):
        """手动暂停/继续轮播"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop()
        else:
            self.timer.start()

    def _next_comment(self):
        """V2.0: 切换到下一条评论（带智能间隔和动画）"""
        if self.is_paused:
            return

        # 智能间隔：根据评论长度调整
        comment_length = len(self.decrypted_comments[self.current_index].content)
        interval = self._calculate_smart_interval(comment_length)

        self.timer.setInterval(interval)

        # 带动画的切换
        self._animate_comment_switch()

        self.current_index = (self.current_index + 1) % len(self.decrypted_comments)
```

---

#### 2.2.5 V2.0 Crypto模块设计

**职责**: 实现评论接口的AES+RSA混合加密算法

**模块结构**:
```
crypto/
├── __init__.py              # 模块初始化
├── crypto_manager.py       # 统一加密接口
├── aes_encryptor.py        # AES加密实现
├── aes_decryptor.py        # AES解密实现
├── rsa_encryptor.py        # RSA加密实现
├── rsa_decryptor.py        # RSA解密实现
├── key_storage.py          # 密钥管理
└── encryption_utils.py     # 加密工具函数
```

##### 2.2.5.1 加密管理器 (crypto_manager.py)

```python
from .aes_encryptor import AESEncryptor
from .aes_decryptor import AESDecryptor
from .rsa_encryptor import RSAEncryptor
from .rsa_decryptor import RSADecryptor

class CryptoManager:
    """V2.0 加密管理器 - 统一加密接口"""

    def __init__(self):
        self.aes_encryptor = AESEncryptor()
        self.aes_decryptor = AESDecryptor()
        self.rsa_encryptor = RSAEncryptor()
        self.rsa_decryptor = RSADecryptor()
        self.key_storage = KeyStorage()

    def encrypt_comment(self, content: str) -> dict:
        """加密评论内容"""
        # 1. 生成随机AES密钥
        aes_key = self.aes_encryptor.generate_key()

        # 2. 使用AES密钥加密评论内容
        encrypted_content = self.aes_encryptor.encrypt(content, aes_key)

        # 3. 使用RSA公钥加密AES密钥
        encrypted_key = self.rsa_encryptor.encrypt(aes_key)

        # 4. 生成数据签名
        signature = self.rsa_encryptor.sign(content)

        return {
            "content": encrypted_content,
            "encryptedKey": encrypted_key,
            "signature": signature
        }

    def decrypt_comment(self, encrypted_data: dict) -> str:
        """解密评论内容"""
        # 1. 使用RSA私钥解密AES密钥
        aes_key = self.rsa_decryptor.decrypt(encrypted_data["encryptedKey"])

        # 2. 使用AES密钥解密评论内容
        content = self.aes_decryptor.decrypt(
            encrypted_data["content"],
            aes_key
        )

        # 3. 验证数据签名
        if not self.rsa_decryptor.verify_signature(
            content,
            encrypted_data["signature"]
        ):
            raise ValueError("数据签名验证失败")

        return content
```

##### 2.2.5.2 AES加密器 (aes_encryptor.py)

```python
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

class AESEncryptor:
    """AES加密器"""

    def generate_key(self) -> bytes:
        """生成随机AES密钥"""
        return get_random_bytes(32)  # 256位密钥

    def encrypt(self, content: str, key: bytes) -> str:
        """使用AES加密内容"""
        # 将内容转换为字节
        content_bytes = content.encode('utf-8')

        # 生成随机IV
        iv = get_random_bytes(16)

        # 创建AES加密器
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # 填充内容到16字节倍数
        padded_content = self._pad(content_bytes)

        # 加密
        encrypted_bytes = cipher.encrypt(padded_content)

        # 组合IV和加密内容
        result = iv + encrypted_bytes

        # Base64编码
        return base64.b64encode(result).decode('utf-8')

    def _pad(self, data: bytes) -> bytes:
        """PKCS7填充"""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
```

##### 2.2.5.3 RSA加密器 (rsa_encryptor.py)

```python
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

class RSAEncryptor:
    """RSA加密器"""

    def __init__(self):
        # 生成RSA密钥对
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey()
        self.private_key = self.key

    def encrypt(self, data: bytes) -> str:
        """使用RSA公钥加密数据"""
        encrypted = self.public_key.encrypt(
            data,
            RSA.pkcs1_oaep_padding
        )
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> bytes:
        """使用RSA私钥解密数据"""
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = self.private_key.decrypt(
            encrypted_bytes,
            RSA.pkcs1_oaep_padding
        )
        return decrypted

    def sign(self, data: str) -> str:
        """生成数据签名"""
        # 创建SHA256哈希
        h = SHA256.new(data.encode('utf-8'))

        # 生成签名
        signature = pkcs1_15.new(self.private_key).sign(h)

        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, data: str, signature: str) -> bool:
        """验证数据签名"""
        try:
            h = SHA256.new(data.encode('utf-8'))
            signature_bytes = base64.b64decode(signature)
            pkcs1_15.new(self.public_key).verify(h, signature_bytes)
            return True
        except (ValueError, TypeError):
            return False
```

##### 2.2.5.4 密钥存储 (key_storage.py)

```python
import json
import os
from pathlib import Path

class KeyStorage:
    """密钥存储管理"""

    def __init__(self):
        self.key_dir = Path.home() / ".music-comment" / "keys"
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_file = self.key_dir / "private_key.pem"
        self.public_key_file = self.key_dir / "public_key.pem"

    def save_keys(self, key_pair):
        """保存RSA密钥对"""
        with open(self.private_key_file, 'wb') as f:
            f.write(key_pair.export_key())

        with open(self.public_key_file, 'wb') as f:
            f.write(key_pair.publickey().export_key())

    def load_private_key(self):
        """加载私钥"""
        if not self.private_key_file.exists():
            return None

        from Crypto.PublicKey import RSA
        with open(self.private_key_file, 'rb') as f:
            return RSA.import_key(f.read())

    def load_public_key(self):
        """加载公钥"""
        if not self.public_key_file.exists():
            return None

        from Crypto.PublicKey import RSA
        with open(self.public_key_file, 'rb') as f:
            return RSA.import_key(f.read())
```

---

#### 2.2.6 解密线程 (decrypt_thread.py) - V2.0新增

```python
from PyQt6.QtCore import QThread, pyqtSignal

class DecryptThread(QThread):
    """解密线程 - 避免UI卡顿"""

    finished = pyqtSignal(list)
    progress = pyqtSignal(int)

    def __init__(self, encrypted_comments, crypto_manager):
        super().__init__()
        self.encrypted_comments = encrypted_comments
        self.crypto_manager = crypto_manager

    def run(self):
        """执行解密任务"""
        decrypted_comments = []

        for i, comment_data in enumerate(self.encrypted_comments):
            try:
                # 解密评论内容
                content = self.crypto_manager.decrypt_comment(comment_data)

                # 创建解密后的评论对象
                comment = Comment(
                    content=content,
                    user=comment_data["user"]["nickname"],
                    likes=comment_data["likedCount"]
                )

                decrypted_comments.append(comment)

                # 发送进度信号
                self.progress.emit(i + 1)

            except Exception as e:
                logger.error(f"解密评论失败: {e}")
                # 使用加密内容作为降级方案
                comment = Comment(
                    content="[解密失败]",
                    user=comment_data["user"]["nickname"],
                    likes=comment_data["likedCount"]
                )
                decrypted_comments.append(comment)

        # 发送完成信号
        self.finished.emit(decrypted_comments)
```

---

#### 2.2.7 配置管理 (settings.py) - V2.0增强

**核心类** - V2.0增强:
```python
@dataclass
class AppConfig:
    """V2.0 增强版应用配置"""
    # 窗口配置
    window_width: int = 320
    window_height: int = 180
    window_opacity: float = 0.85

    # 轮播配置（V2.0增强）
    rotation_interval: int = 5000  # 毫秒
    rotation_animation_duration: int = 500  # 毫秒
    rotation_auto_pause: bool = True  # 自动暂停
    rotation_manual_pause: bool = True  # 手动暂停
    rotation_smart_interval: bool = True  # 智能间隔
    rotation_min_interval: int = 3000  # 最小间隔（毫秒）
    rotation_max_interval: int = 10000  # 最大间隔（毫秒）
    rotation_memory_position: bool = True  # 记忆位置

    # 评论显示配置（V2.0新增）
    show_real_comments: bool = True  # 显示真实评论
    show_encrypted_comments: bool = False  # 显示加密评论（调试用）
    decryption_timeout: int = 10000  # 解密超时（毫秒）

    # 加密配置（V2.0新增）
    encryption_enabled: bool = True
    encryption_algorithm: str = "AES+RSA"  # 加密算法
    aes_key_size: int = 256  # AES密钥长度
    rsa_key_size: int = 2048  # RSA密钥长度

    # API配置
    api_base_url: str = "http://localhost:3000"
    api_timeout: int = 10
    max_retries: int = 3

    # 缓存配置
    cache_size: int = 50
    comment_cache_time: int = 3600  # 秒

    @classmethod
    def load(cls) -> "AppConfig":
        """从配置文件加载"""
        pass

    def save(self) -> None:
        """保存到配置文件"""
        pass
```

---

#### 2.2.5 数据模型 (models/)

**歌曲信息模型 (song_info.py)**:
```python
from dataclasses import dataclass
from typing import List

@dataclass
class SongInfo:
    """歌曲信息"""
    song_id: str
    name: str
    artist: str
    album: str = ""
    genres: List[str] = None
    duration: int = 0

    def __post_init__(self):
        if self.genres is None:
            self.genres = []

    def get_genres_str(self) -> str:
        """获取风格字符串"""
        return " / ".join(self.genres) if self.genres else "未知风格"
```

**评论模型 (comment.py)**:
```python
from dataclasses import dataclass

@dataclass
class Comment:
    """评论信息"""
    content: str
    user: str
    likes: int
    time: str = ""
```

---

#### 2.2.6 配置管理 (settings.py)

**职责**: 管理应用配置

**核心类**:
```python
@dataclass
class AppConfig:
    """应用配置"""
    # 窗口配置
    window_width: int = 320
    window_height: int = 180
    window_opacity: float = 0.85

    # 轮播配置
    rotation_interval: int = 5000  # 毫秒
    animation_duration: int = 500   # 毫秒

    # API配置
    api_base_url: str = "http://localhost:3000"
    api_timeout: int = 10
    max_retries: int = 3

    # 缓存配置
    cache_size: int = 50
    comment_cache_time: int = 3600  # 秒

    @classmethod
    def load(cls) -> "AppConfig":
        """从配置文件加载"""
        pass

    def save(self) -> None:
        """保存到配置文件"""
        pass
```

**配置文件路径**:
```
~/.music-comment/config.json
```

---

## 3. 数据库设计

本项目**不使用数据库**，使用以下存储方式：

### 3.1 内存缓存

**缓存类型**: LRU Cache (Least Recently Used)

**缓存内容**:
1. **歌曲搜索结果**: `(song_name, artist_name) -> song_id`
2. **歌曲详情**: `song_id -> SongInfo`
3. **热门评论**: `song_id -> List[Comment]`

**缓存大小**: 50 条

**缓存时间**:
- 歌曲详情: 86400 秒（24小时）
- 热门评论: 3600 秒（1小时）

### 3.2 文件存储

**配置文件**: `~/.music-comment/config.json`

```json
{
  "window": {
    "width": 320,
    "height": 180,
    "opacity": 0.85
  },
  "rotation": {
    "interval": 5000,
    "animation_duration": 500
  },
  "api": {
    "base_url": "http://localhost:3000",
    "timeout": 10,
    "max_retries": 3
  }
}
```

---

## 4. 接口设计

### 4.1 内部接口

#### 4.1.1 Monitor → APIClient

```python
# Monitor 调用 APIClient 搜索歌曲
song_id = api_client.search_song("浪人情歌", "伍佰")

# 返回值
str: "2700274699"
None: 搜索失败
```

#### 4.1.2 APIClient → GUI

```python
# APIClient 返回数据给 GUI
song_info = api_client.get_song_detail("2700274699")
comments = api_client.get_hot_comments("2700274699")

# GUI 更新显示
comment_widget.update_song(song_info, comments)
```

### 4.2 外部接口

#### 4.2.1 NeteaseCloudMusicApi

**搜索歌曲**:
```http
GET /search?keywords={song_name} {artist_name}
Host: localhost:3000
```

**获取热门评论**:
```http
GET /comment/hot?id={song_id}&limit=20
Host: localhost:3000
```

**获取歌曲详情**:
```http
GET /song/detail?ids={song_id}
Host: localhost:3000
```

#### 4.2.2 Windows API

**枚举窗口**:
```python
win32gui.EnumWindows(callback, param)
```

**获取窗口标题**:
```python
title = win32gui.GetWindowText(hwnd)
```

**获取窗口类名**:
```python
class_name = win32gui.GetClassName(hwnd)
```

**获取进程ID**:
```python
_, pid = win32process.GetWindowThreadProcessId(hwnd)
```

---

## 5. 部署设计

### 5.1 开发环境

**目录结构**:
```
music-comment/
├── .venv/              # 虚拟环境
├── logs/               # 日志输出
├── src/                # 源代码
├── tests/              # 测试代码
├── scripts/            # 启动脚本
├── docs/               # 文档
├── discuss/            # 讨论文档
├── pyproject.toml      # 项目配置
└── README.md
```

**环境准备**:
```bash
# 1. 创建虚拟环境
uv venv

# 2. 激活虚拟环境
.venv\Scripts\activate

# 3. 安装依赖
uv pip install -r requirements.txt

# 4. 部署 API 服务（另开终端）
cd NeteaseCloudMusicApi
npm install
npm start
```

### 5.2 生产环境

**打包方案**: PyInstaller

**打包命令**:
```bash
pyinstaller --onefile --windowed ^
  --name "MusicComment" ^
  --icon=assets/icon.ico ^
  --add-data "src;src" ^
  --hidden-import=PyQt6 ^
  src/main.py
```

**安装包结构**:
```
MusicComment/
├── MusicComment.exe    # 主程序
├── config.json         # 配置文件（可选）
└── README.txt          # 使用说明
```

**安装步骤**:
1. 解压安装包到任意目录
2. （首次运行）启动 NeteaseCloudMusicApi 服务
3. 双击 MusicComment.exe 启动应用

---

## 6. 性能优化

### 6.1 缓存策略

**LRU 缓存实现**:
```python
from functools import lru_cache

class NeteaseAPIClient:
    @lru_cache(maxsize=50)
    def get_song_detail(self, song_id: str):
        # 优先从缓存读取
        pass

    def clear_cache(self):
        # 清空缓存
        self.get_song_detail.cache_clear()
```

**缓存失效策略**:
- 时间失效：TTL（Time To Live）
- 空间失效：LRU（Least Recently Used）
- 手动失效：切歌时清除旧数据

### 6.2 网络优化

**请求优化**:
1. **连接复用**: 使用 `requests.Session()`
2. **超时控制**: 每个请求 10 秒超时
3. **重试机制**: 最多重试 3 次
4. **频率限制**: 请求间隔 ≥ 1 秒

**代码示例**:
```python
class NeteaseAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_interval = 1.0  # 最小请求间隔

    def _rate_limit(self):
        """请求频率限制"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = now
```

### 6.3 内存优化

**内存控制**:
- 评论列表只保留当前歌曲的 20 条
- 缓存最多 50 首歌曲的信息
- 定期清理过期数据

**代码示例**:
```python
class CommentWidget:
    def update_song(self, song, comments):
        # 切歌时清理旧数据
        if self.current_song != song:
            self.comments.clear()

        # 只保留前 20 条
        self.comments = comments[:20]
```

---

## 7. 安全设计

### 7.1 数据安全

**隐私保护**:
- ❌ 不收集用户数据
- ❌ 不上传任何信息到远程服务器
- ✅ 所有数据仅存储在本地
- ✅ 配置文件明文存储（无敏感信息）

### 7.2 网络安全

**通信安全**:
- 仅访问本地 API 服务（localhost:3000）
- 不访问任何外部网络服务
- API 请求不包含用户凭证

### 7.3 代码安全

**输入验证**:
```python
def parse_window_title(title: str) -> dict:
    """解析窗口标题，验证输入"""
    if not title or not isinstance(title, str):
        return None

    if ' - ' not in title:
        return None

    # 防止恶意输入
    if len(title) > 200:
        return None

    # 解析...
```

**错误处理**:
```python
def safe_api_call(func):
    """安全的 API 调用装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"API 请求失败: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON 解析失败: {e}")
            return None
    return wrapper
```

---

## 8. 日志设计

### 8.1 日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 调试信息 | "找到窗口: 句柄=12345" |
| INFO | 正常信息 | "成功识别歌曲: 浪人情歌" |
| WARNING | 警告信息 | "API 请求失败，使用缓存" |
| ERROR | 错误信息 | "网易云窗口未找到" |

### 8.2 日志格式

```python
[2024-12-30 10:30:45] [INFO] [monitor.py:45] 成功识别歌曲: 浪人情歌 - 伍佰
[2024-12-30 10:30:46] [INFO] [api_client.py:78] 获取评论成功: 20条
```

### 8.3 日志文件

**日志路径**:
```
logs/
├── music-comment-2024-12-30.log    # 当天日志
├── music-comment-2024-12-29.log    # 历史日志
└── music-comment.log               # 当前日志（软链接）
```

**日志轮转**:
- 每天一个日志文件
- 保留最近 30 天的日志
- 单个文件最大 10MB

---

## 9. 测试设计

### 9.1 单元测试

**测试覆盖率目标**: ≥ 70%

**测试文件**:
```
tests/
├── test_monitor.py       # 窗口监控模块测试
├── test_api_client.py    # API客户端测试
├── test_models.py        # 数据模型测试
└── test_widgets.py       # GUI组件测试
```

**测试示例**:
```python
# test_monitor.py
def test_parse_window_title():
    """测试窗口标题解析"""
    monitor = NeteaseWindowMonitor()

    # 正常情况
    result = monitor.parse_window_title("浪人情歌 - 伍佰")
    assert result['song_name'] == "浪人情歌"
    assert result['artist_name'] == "伍佰"

    # 异常情况
    result = monitor.parse_window_title("invalid title")
    assert result is None
```

### 9.2 集成测试

**测试场景**:
1. 正常播放：识别 → 搜索 → 获取评论 → 显示
2. 切歌：更新识别 → 清除缓存 → 重新获取
3. 网易云关闭：优雅降级 → 提示用户
4. API 失败：使用缓存 → 记录日志

### 9.3 性能测试

**测试指标**:
- 启动时间 < 3 秒
- 内存占用 < 100 MB
- CPU 占用 < 5%（空闲时）

---

## 10. 错误处理

### 10.1 错误分类

| 错误类型 | 处理方式 | 用户体验 |
|----------|----------|----------|
| 网易云未运行 | 提示用户启动网易云 | 弹窗提示 |
| 窗口未找到 | 重试 3 次，失败后记录日志 | 暂停更新 |
| API 请求失败 | 使用缓存数据 | 显示缓存评论 |
| JSON 解析失败 | 返回空数据 | 显示"暂无评论" |
| 网络超时 | 重试 3 次，指数退避 | 延迟显示 |

### 10.2 异常处理策略

```python
class ErrorHandler:
    """错误处理器"""

    @staticmethod
    def handle_netease_not_found():
        """处理网易云未运行"""
        QMessageBox.warning(
            None,
            "网易云音乐未运行",
            "请启动网易云音乐后再使用本应用"
        )

    @staticmethod
    def handle_api_error(error):
        """处理 API 错误"""
        logger.error(f"API 错误: {error}")
        # 尝试使用缓存数据
        return cache.get("last_comments")
```

---

## 11. 维护指南

### 11.1 日志分析

**常见问题排查**:
1. **无法识别歌曲**:
   - 检查日志：`grep "网易云窗口" logs/music-comment.log`
   - 确认网易云是否运行
   - 确认窗口类名是否为 `OrpheusBrowserHost`

2. **无法获取评论**:
   - 检查日志：`grep "API 请求" logs/music-comment.log`
   - 确认 API 服务是否运行
   - 测试 API：`curl http://localhost:3000/comment/hot?id=xxx`

3. **应用卡顿**:
   - 检查内存使用：`tasklist /FI "IMAGENAME eq MusicComment.exe"`
   - 清除缓存：删除 `~/.music-comment/cache/`

### 11.2 版本升级

**升级流程**:
1. 备份配置文件：`cp ~/.music-comment/config.json ~/.music-comment/config.json.bak`
2. 卸载旧版本
3. 安装新版本
4. 恢复配置文件

---

## 12. 附录

### 12.1 开发规范

**代码风格**:
- 遵循 PEP 8 规范
- 使用 Google Style Guide 文档字符串
- 单文件代码行数 < 300
- 函数代码行数 < 50

**命名规范**:
```python
# 类名：大驼峰
class NetaseWindowMonitor:

# 函数名：小写+下划线
def get_current_song():

# 常量：全大写
MAX_CACHE_SIZE = 50

# 私有方法：前缀下划线
def _parse_title():
```

### 12.2 性能基准

| 操作 | 目标时间 | 实际时间 |
|------|----------|----------|
| 启动应用 | < 3 秒 | 待测试 |
| 识别歌曲 | < 1 秒 | 待测试 |
| 获取评论 | < 2 秒 | 待测试 |
| 切换评论 | < 500ms | 待测试 |

### 12.3 参考资料

**技术文档**:
- [PyQt6 官方文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Windows API](https://docs.python.org/3/library/windows.html)
- [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)

**设计模式**:
- **分层架构**: MVC 变体
- **缓存模式**: LRU Cache
- **单例模式**: Config Manager
- **观察者模式**: 评论轮播

---

**文档结束**
