#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础服务模块
"""

from app.common.logging.logger import log_manager


class BaseService:
    """基础服务类"""
    
    def __init__(self, service_name: str):
        """初始化服务
        
        Args:
            service_name (str): 服务名称
        """
        self.logger = log_manager.get_logger(service_name)
