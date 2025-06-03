#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志管理模块
"""

import os
import sys
from loguru import logger
from app.config import settings

# 确保日志目录存在
os.makedirs(settings.LOG_DIR, exist_ok=True)

# 配置日志输出格式
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


class LogManager:
    """日志管理器"""

    def __init__(self):
        # 清除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format=LOG_FORMAT,
            level=settings.LOG_LEVEL,
            colorize=True,
        )
        
        # 添加文件处理器
        logger.add(
            os.path.join(settings.LOG_DIR, "app_{time}.log"),
            rotation="10 MB",  # 日志文件大小达到10MB时轮转
            retention="7 days",  # 保留7天的日志
            format=LOG_FORMAT,
            level=settings.LOG_LEVEL,
            compression="zip",  # 压缩旧日志文件
        )

    def get_logger(self, name=None):
        """获取logger实例
        
        Args:
            name: 可选的日志记录器名称
            
        Returns:
            logger: loguru日志记录器实例
        """
        if name:
            # 在loguru中，name并不会创建新的logger实例，
            # 而是会被用作上下文信息显示在日志中
            return logger.bind(name=name)
        return logger


# 创建全局日志管理器实例
log_manager = LogManager()
