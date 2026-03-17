#!/usr/bin/env python3
"""
日志模块
"""

import os
import logging
import logging.handlers
from datetime import datetime


def setup_logger(level: str = "INFO", log_file: str = "logs/autojob.log") -> logging.Logger:
    """设置日志"""
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger("AutoJob")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger
