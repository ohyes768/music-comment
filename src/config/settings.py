"""
全局配置管理

负责应用的全局配置，包括窗口设置、轮播设置、API设置、缓存设置等
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """应用配置数据类

    包含应用的所有配置项，窗口设置、轮播设置、API设置、缓存设置等
    """
    # 窗口配置
    window_width: int = 320    # 窗口宽度（更窄）
    window_height: int = 200   # 窗口高度（紧凑）
    window_opacity: float = 0.95  # 窗口透明度（0.95=95%不透明，更清晰）

    # 轮播配置
    rotation_interval: int = 8000  # 毫秒（8秒）
    animation_duration: int = 500   # 毫秒

    # 爬虫配置
    # 注意：使用网易云官方 Web API，无需本地 API 服务
    api_timeout: int = 10
    max_retries: int = 3

    # 缓存配置
    cache_size: int = 50
    comment_cache_time: int = 3600  # 秒

    # 风格标签配置（MVP版本）
    max_genre_tags: int = 3          # 最多显示的标签数
    default_genre: str = "未知风格"  # 默认风格标签

    @classmethod
    def get_config_path(cls) -> Path:
        """获取配置文件路径

        Returns:
            Path: 配置文件的完整路径
        """
        config_dir = Path.home() / ".music-comment"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def load(cls) -> "AppConfig":
        """从配置文件加载配置

        如果配置文件不存在，则返回默认配置

        Returns:
            AppConfig: 加载的配置对象
        """
        config_path = cls.get_config_path()

        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"配置文件格式错误，使用默认配置: {e}")
            return cls()

    def save(self) -> None:
        """保存配置到文件"""
        config_path = self.get_config_path()

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)


# 全局配置单例
_global_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """获取全局配置单例

    Returns:
        AppConfig: 全局配置对象
    """
    global _global_config

    if _global_config is None:
        _global_config = AppConfig.load()

    return _global_config


def reload_config() -> AppConfig:
    """重新加载配置文件

    Returns:
        AppConfig: 重新加载的配置对象
    """
    global _global_config
    _global_config = AppConfig.load()
    return _global_config
