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
        async def recognize_intent(request: IntentRecognizeRequest):
            """识别意图接口
            
            Args:
                request (IntentRecognizeRequest): 意图识别请求
                
            Returns:
                dict: 意图识别响应，格式为：
                {
                  "success": true,
                  "message": "Success",
                  "data": {
                    "intent": "INTENT_TYPE",
                    "confidence": "0.9",
                    "query": "用户输入的原始文本",
                    "result": {
                      # 触发指定action后返回的数据
                    }
                  }
                }
            """
            try:
                # 调用意图服务进行识别
                response = await self.intent_service.recognize_intent(
                    text=request.text,
                    context=request.context,
                    session_id=request.session_id
                )
                
                # 使用to_dict方法生成响应格式
                result = response.to_dict()
                
                # 确保所有字段都存在且类型正确
                if "data" not in result or not isinstance(result["data"], dict):
                    result["data"] = {}
                
                data = result["data"]
                if "intent" not in data or data["intent"] is None:
                    data["intent"] = "UNKNOWN"
                
                if "confidence" not in data or data["confidence"] is None:
                    data["confidence"] = "0.0"
                
                if "query" not in data or data["query"] is None:
                    data["query"] = request.text or ""
                
                if "result" not in data:
                    data["result"] = {}
                
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
                        "query": request.text or "",
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
