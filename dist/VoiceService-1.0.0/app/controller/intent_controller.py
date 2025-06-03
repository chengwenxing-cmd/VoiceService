#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图控制器模块
"""

from fastapi import APIRouter
from app.common.logging.logger import log_manager
from app.controller.base_controller import BaseController
from app.service.intent_service import IntentService
from app.service.dialogue_context_service import dialogue_context_service
from app.domain.value_object.request_response import IntentRecognizeRequest
from app.common.utils.response import ResponseUtil
from pydantic import BaseModel
from typing import Optional
from fastapi import Request


# 定义设备位置请求模型
class DeviceLocationRequest(BaseModel):
    """设备位置请求模型"""
    city: str
    province: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class IntentController(BaseController):
    """意图控制器"""
    
    def __init__(self):
        """初始化意图控制器"""
        super().__init__("/intent")
        self.intent_service = IntentService()
        self.logger = log_manager.get_logger("intent_controller")
        self._register_routes()
    
    def _register_routes(self):
        """注册路由"""
        
        @self.router.post("/recognize")
        async def recognize_intent(request: Request, data: IntentRecognizeRequest):
            """识别意图接口
            
            Args:
                request (Request): FastAPI请求对象，用于获取客户端IP
                data (IntentRecognizeRequest): 意图识别请求
                
            Returns:
                dict: 意图识别响应
            """
            try:
                # 获取客户端IP地址
                client_ip = request.client.host if request.client else "127.0.0.1"
                self.logger.info(f"接收到来自 {client_ip} 的意图识别请求，文本: '{data.text}', 会话ID: {data.session_id}")
                
                # 添加IP地址到上下文
                context = data.context or {}
                if "metadata" not in context:
                    context["metadata"] = {}
                context["metadata"]["client_ip"] = client_ip
                
                # 调用意图服务进行识别
                response = await self.intent_service.recognize_intent(
                    text=data.text,
                    context=context,
                    session_id=data.session_id
                )
                
                # 使用to_dict方法生成响应格式
                result = response.to_dict()
                
                # 确保所有字段都存在且类型正确
                if "data" not in result or not isinstance(result["data"], dict):
                    result["data"] = {}
                
                data_result = result["data"]
                if "intent" not in data_result or data_result["intent"] is None:
                    data_result["intent"] = "UNKNOWN"
                
                if "confidence" not in data_result or data_result["confidence"] is None:
                    data_result["confidence"] = "0.0"
                
                if "query" not in data_result or data_result["query"] is None:
                    data_result["query"] = data.text or ""
                
                if "result" not in data_result:
                    data_result["result"] = {}
                
                return result
            except Exception as e:
                self.logger.error(f"处理意图识别请求失败: {str(e)}")
                # 返回错误响应
                return {
                    "success": False,
                    "message": f"处理失败: {str(e)}",
                    "data": {
                        "intent": "ERROR",
                        "confidence": "0.0",
                        "query": data.text or "",
                        "result": {
                            "status": "error",
                            "message": str(e),
                            "code": 500,
                            "data": {}
                        }
                    }
                }
                
        @self.router.post("/location")
        async def update_device_location(request: DeviceLocationRequest, session_id: str = "default"):
            """更新设备位置信息
            
            Args:
                request (DeviceLocationRequest): 设备位置请求
                session_id (str, optional): 会话ID. 默认为"default".
                
            Returns:
                dict: 更新结果
            """
            try:
                # 设置设备位置
                dialogue_context_service.set_device_location(
                    session_id=session_id,
                    city=request.city,
                    province=request.province,
                    latitude=request.latitude,
                    longitude=request.longitude
                )
                
                # 返回成功响应
                return {
                    "success": True,
                    "message": f"设备位置已更新: {request.city}",
                    "data": {
                        "session_id": session_id,
                        "location": {
                            "city": request.city,
                            "province": request.province,
                            "latitude": request.latitude,
                            "longitude": request.longitude
                        }
                    }
                }
            except Exception as e:
                self.logger.error(f"更新设备位置失败: {str(e)}")
                # 返回错误响应
                return {
                    "success": False,
                    "message": f"更新位置失败: {str(e)}",
                    "data": {
                        "session_id": session_id
                    }
                }
                
        @self.router.get("/location")
        async def get_device_location(session_id: str = "default"):
            """获取设备位置信息
            
            Args:
                session_id (str, optional): 会话ID. 默认为"default".
                
            Returns:
                dict: 设备位置信息
            """
            try:
                # 获取设备位置
                location = dialogue_context_service.get_device_location(session_id)
                
                # 返回成功响应
                return {
                    "success": True,
                    "message": "获取设备位置成功",
                    "data": {
                        "session_id": session_id,
                        "location": location
                    }
                }
            except Exception as e:
                self.logger.error(f"获取设备位置失败: {str(e)}")
                # 返回错误响应
                return {
                    "success": False,
                    "message": f"获取位置失败: {str(e)}",
                    "data": {
                        "session_id": session_id
                    }
                }


# 创建全局路由实例
router = APIRouter(prefix="/intent", tags=["意图识别"])

# 实例化控制器并获取路由
controller = IntentController()
router = controller.router
