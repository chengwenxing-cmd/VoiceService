#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
请求响应值对象模块
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.domain.entity.intent import Intent
from app.domain.entity.action import Action


class IntentRecognizeRequest(BaseModel):
    """意图识别请求"""
    
    text: str = Field(..., description="需要识别的文本")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="可选的上下文信息"
    )
    session_id: str = Field(
        default="default",
        description="会话ID，用于跟踪对话上下文"
    )


class IntentRecognizeResponse(BaseModel):
    """意图识别响应"""
    
    intent: Intent
    action: Action
    result: Dict[str, Any] = Field(default_factory=dict, description="动作执行结果")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        # 格式化意图类型为大写字符串
        intent_type = str(self.intent.type.value).upper()
        
        # 格式化置信度为字符串，保留两位小数
        confidence = str(round(self.intent.confidence, 2))
        
        # 确保query字段不为None
        query = self.intent.text if self.intent.text else ""
        
        return {
            "success": True,
            "message": "Success",
            "data": {
                "intent": intent_type,
                "confidence": confidence,
                "query": query,
                "result": self.result
            }
        }
