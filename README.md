# 网易云音乐评论桌面应用

> 获取当前播放歌曲的热门评论，以小窗口透明悬浮方式展示，适合摸鱼使用！

## 项目简介

一个 Windows 桌面应用，通过读取网易云音乐窗口标题，自动获取当前播放歌曲的信息和热门评论，并以透明悬浮窗口展示，评论每隔 8 秒自动切换。

**数据获取方式**: 直接调用网易云 Web API，实现了 AES+RSA 加密算法，无需本地部署第三方 API 服务

## 功能特性

- ✅ **自动识别歌曲**: 通过窗口标题读取当前播放的歌曲
- ✅ **歌曲信息**: 显示歌曲名、歌手
- ✅ **热门评论**: 真实热门评论，包含用户名和点赞数
- ✅ **评论轮播**: 每 8 秒自动切换到下一条评论
- ✅ **透明悬浮**: 半透明悬浮窗口（320x200），60% 不透明度
- ✅ **可拖动**: 按住鼠标左键拖动窗口到任意位置
- ✅ **可最小化**: 右键菜单或双击窗口最小化/还原
- ✅ **自动更新**: 每 3 秒检测歌曲切换，自动更新显示
- ✅ **摸鱼友好**: 最小化时仍可正常工作

## 技术栈

- **语言**: Python 3.10+
- **GUI**: PyQt6
- **歌曲识别**: Windows API (win32gui)
- **数据获取**: 直接调用网易云 Web API（实现了 AES+RSA 加密）
- **展示**: 透明悬浮窗口（自定义绘制实现半透明背景）

## 开发状态

### ✅ V2版本已完成（2025-01-02）

- [x] 技术方案调研
- [x] 窗口标题读取方案验证
- [x] 项目结构设计
- [x] 爬虫客户端开发（直接调用网易云 Web API）
- [x] **评论接口加密算法实现**（AES-CBC + RSA）
- [x] **真实热门评论获取**
- [x] 评论轮播功能（8 秒间隔）
- [x] GUI 开发完成
- [x] 半透明背景实现（60% 不透明度）
- [x] 核心功能测试通过

## 项目结构

```
music-comment/
├── .venv/                          # Python虚拟环境
├── logs/                           # 日志输出
├── scripts/                        # 启动脚本
│   └── run.bat                     # 批处理脚本
├── src/                            # 源代码
│   ├── config/                     # 配置管理
│   │   └── settings.py             # 全局配置
│   ├── core/                       # 核心逻辑
│   │   ├── monitor.py              # 窗口标题读取
│   │   ├── netease_crawler.py      # 网易云爬虫
│   │   └── crypto.py               # 加密算法（AES+RSA）
│   ├── gui/                        # 图形界面
│   │   ├── main_window.py          # 主窗口
│   │   └── comment_widget.py       # 评论展示组件
│   ├── models/                     # 数据模型
│   │   ├── song_info.py            # 歌曲信息模型
│   │   └── comment.py              # 评论模型
│   ├── utils/                      # 工具函数
│   │   └── logger.py               # 日志工具
│   └── main.py                     # 应用入口
├── tests/                          # 测试代码
│   └── test_v2_complete.py         # V2完整功能测试
├── discuss/                        # 讨论文档
│   └── 2024-12-31_爬虫方案实施总结.md
├── requirements.txt                # 依赖清单
└── README.md
```

## 安装运行

### 环境要求

- Python 3.10+
- Windows 操作系统

### 快速开始

**重要**: 需要以**管理员身份**运行 PowerShell 或命令提示符

```bash
# 1. 以管理员身份运行 PowerShell
# 右键点击 PowerShell -> 选择「以管理员身份运行」

# 2. 进入项目目录
cd F:\github\person_project\music-comment

# 3. 安装依赖（首次运行）
.venv\Scripts\pip.exe install -r requirements.txt

# 4. 启动应用
.\scripts\run.bat
```

**为什么需要管理员权限？**
- 应用需要使用 `win32gui.EnumWindows()` 枚举窗口
- Windows 安全机制要求此操作需要管理员权限

## 界面预览

```
┌──────────────────────────┐
│                          │
│ 浪人情歌 - 伍佰          │
│                          │
│ 这首歌太好听了...        │
│ 每次听都很有感触         │
│                          │
│         ↑                │
│       弹性空间            │
│         ↓                │
│    用户名 · 127  ▶       │  右下角
└──────────────────────────┘
```

## 配置说明

所有配置项都在 `src/config/settings.py` 中：

```python
# 窗口配置
window_width: int = 320        # 窗口宽度
window_height: int = 200       # 窗口高度
# window_opacity: float = 0.95  # 已弃用，改用 alpha 通道

# 轮播配置
rotation_interval: int = 8000  # 评论轮播间隔（毫秒）

# 爬虫配置
api_timeout: int = 10          # API 超时时间（秒）
max_retries: int = 3           # 最大重试次数

# 缓存配置
cache_size: int = 50           # 缓存大小
comment_cache_time: int = 3600  # 评论缓存时间（秒）
```

## 注意事项

1. **网易云音乐必须运行**: 应用需要读取网易云窗口标题
2. **网络连接**: 获取歌曲信息需要网络
3. **合理使用**: 请遵守网易云音乐 API 使用规范，避免频繁请求

## 技术亮点

### 1. 评论接口加密算法

成功逆向并实现了网易云音乐的评论接口加密：

- **AES-CBC 加密**: 双重 AES 加密实现参数加密
- **RSA 加密**: 公钥加密实现密钥交换
- **固定参数优化**: 固定随机字符串，减少计算量

**参考文章**:
- [Python爬虫练习：爬取网易云音乐评论(2024附完整代码)](https://blog.csdn.net/Lywan666/article/details/136632883)
- [网易云音乐搜索接口JS逆向](https://developer.aliyun.com/article/1596740)

### 2. 半透明背景实现

使用 PyQt6 的自定义绘制实现真正的半透明效果：

- 设置 `WA_TranslucentBackground` 属性
- 重写 `paintEvent` 方法
- 使用 `QPainter` 绘制带 alpha 通道的背景
- 实现圆角矩形背景（60% 不透明度）

## 依赖清单

```
PyQt6==6.10.1          # GUI框架
requests==2.32.5       # HTTP请求
pycryptodome==3.23.0   # 加密算法
pywin32==311           # Windows API
psutil==7.2.1          # 系统进程信息
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- 网易云音乐 - 数据来源

---

**状态**: ✅ V2版本已完成，可直接运行

**最后更新**: 2025-01-02

**版本**: v2.0.0

