"""
日志工具

提供统一的日志记录功能，输出到控制台和文件
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "music-comment",
    level: int = logging.INFO,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_dir: 日志文件目录，默认为 logs/

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    if log_dir is None:
        log_dir = Path("logs")

    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（每天一个文件）
    log_file = log_dir / f"music-comment-{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 全局日志记录器
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """获取全局日志记录器

    Returns:
        logging.Logger: 全局日志记录器
    """
    global _logger

    if _logger is None:
        _logger = setup_logger()

    return _logger
