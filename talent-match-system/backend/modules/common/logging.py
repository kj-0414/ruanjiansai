"""
日志配置模块
提供统一的日志管理
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from modules.common import get_settings


def setup_logging() -> None:
    """
    配置全局日志系统
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 根日志记录器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除默认处理器
    root_logger.handlers.clear()
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果配置了）
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_path,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 为常见的第三方库设置较高的日志级别，减少噪音
    for lib_name in ['urllib3', 'requests', 'sqlalchemy', 'httpx']:
        logging.getLogger(lib_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取命名的日志记录器
    
    Args:
        name: 日志记录器名称，通常用 __name__
    
    Returns:
        配置好的 Logger 实例
    """
    return logging.getLogger(name)
