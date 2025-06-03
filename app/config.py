#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序配置模块 - 简化版，不依赖pydantic-settings
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    """应用程序配置类"""
    
    def __init__(self):
        # 应用信息
        self.APP_NAME = "VoiceService"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
        
        # 服务器设置
        self.SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
        
        # 大模型配置
        self.DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
        self.QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen-max")
        
        # 第三方API配置
        self.AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")  # 高德地图API密钥
        
        # 数据库配置
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voice_service.db")
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_DIR = os.getenv("LOG_DIR", "logs")


# 创建全局设置实例
settings = Settings()
