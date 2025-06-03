#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from app.config import settings
from app.controller.intent_controller import router as intent_router
from app.controller.base_controller import BaseController
from app.common.exception import AppException

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="语音意图识别服务API",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(AppException, BaseController.app_exception_handler)
app.add_exception_handler(Exception, BaseController.general_exception_handler)

# 注册路由
app.include_router(intent_router, prefix="/api")

# 静态文件目录
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# 健康检查接口
@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "success": True,
        "message": "Service is healthy",
        "data": {
            "status": "up",
            "version": settings.APP_VERSION
        }
    }


# 根路径重定向到测试页面
@app.get("/")
async def root():
    """将根路径重定向到测试页面"""
    return RedirectResponse(url="/static/index.html")
