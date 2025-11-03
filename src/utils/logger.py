"""日志工具模块。

提供统一的日志配置和管理。
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_file: Optional[str] = None, log_level: int = logging.INFO) -> None:
    """设置日志配置。
    
    Args:
        log_file: 日志文件路径，如果为 None 则只输出到控制台
        log_level: 日志级别，默认 INFO
    """
    # 创建日志目录
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志记录器
    handlers = []
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(console_handler)
    
    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format=log_format,
        datefmt=date_format
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('pyodbc').setLevel(logging.WARNING)
    logging.getLogger('PyQt6').setLevel(logging.WARNING)

