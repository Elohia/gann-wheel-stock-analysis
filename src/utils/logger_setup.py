#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志设置模块

配置和初始化系统日志记录功能。

Author: AI Assistant
Date: 2024
"""

import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def setup_logger(logging_config: Dict[str, Any]) -> None:
    """
    设置日志记录器
    
    Args:
        logging_config: 日志配置字典
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 获取配置参数
    log_level = logging_config.get('level', 'INFO')
    log_file = logging_config.get('file_path', 'logs/stock_analysis.log')
    max_size = logging_config.get('max_size', '10MB')
    backup_count = logging_config.get('backup_count', 5)
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True
    )
    
    # 添加文件处理器
    logger.add(
        log_file,
        format=file_format,
        level=log_level,
        rotation=max_size,
        retention=backup_count,
        compression="zip",
        encoding="utf-8"
    )
    
    logger.info(f"日志系统初始化完成，级别: {log_level}，文件: {log_file}")


def get_logger(name: str = None):
    """
    获取日志记录器实例
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    if name:
        return logger.bind(name=name)
    return logger