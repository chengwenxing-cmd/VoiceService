#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础控制器模块
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.common.exception import AppException
from app.common.utils.response import ResponseUtil
from app.common.logging.logger import log_manager

# 创建日志器
logger = log_manager.get_logger("controller")


class BaseController:
    """基础控制器类"""
    
    def __init__(self, prefix: str):
        """初始化控制器
        
        Args:
            prefix (str): 路由前缀
        """
        self.router = APIRouter(prefix=prefix)
    
    @staticmethod
    async def app_exception_handler(request: Request, exc: AppException):
        """应用异常处理器"""
        logger.error(f"应用异常: {exc.message}, 代码: {exc.code}")
        return JSONResponse(
            status_code=exc.code,
            content=ResponseUtil.error(message=exc.message, code=exc.code)
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        logger.error(f"未捕获的异常: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseUtil.error(message="服务器内部错误")
        )
