#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大模型服务模块
"""

from typing import Dict, Any, Optional, List

from app.service.base_service import BaseService
from app.adapters.llm.qwen_client import QwenClient
from app.common.exception import LLMException


class LLMService(BaseService):
    """大模型服务"""
    
    def __init__(self):
        """初始化大模型服务"""
        super().__init__("llm_service")
        
        try:
            # 初始化千问客户端
            self.qwen_client = QwenClient()
            self.logger.info("大模型服务初始化成功")
        except Exception as e:
            self.logger.error(f"大模型服务初始化失败: {str(e)}")
            raise
    
    async def recognize_intent(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None,
        message_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """识别文本的意图
        
        Args:
            text (str): 待识别的文本
            context (Optional[Dict[str, Any]], optional): 上下文信息. 默认为None.
            message_history (Optional[List[Dict[str, str]]], optional): 消息历史. 默认为None.
            
        Returns:
            Dict[str, Any]: 意图识别结果
            
        Raises:
            LLMException: 调用大模型失败时抛出
        """
        try:
            # 调用千问大模型进行意图识别
            result = await self.qwen_client.intent_recognition(text, context, message_history)
            return result
                
        except Exception as e:
            error_msg = f"意图识别失败: {str(e)}"
            self.logger.error(error_msg)
            raise LLMException(error_msg)
