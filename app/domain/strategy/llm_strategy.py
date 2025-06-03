#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于大模型的意图识别策略
"""

from typing import Dict, Any, List, Optional

from app.domain.strategy.base_strategy import IntentStrategy
from app.domain.entity.intent import Intent, IntentType
from app.service.llm_service import LLMService


class LLMBasedStrategy(IntentStrategy):
    """基于大模型的意图识别策略"""
    
    def __init__(self, llm_service: LLMService):
        """初始化
        
        Args:
            llm_service (LLMService): 大模型服务
        """
        self.llm_service = llm_service
    
    async def recognize(self, text: str, context: Optional[Dict[str, Any]], 
                      history: Optional[List[Dict[str, Any]]]) -> Optional[Intent]:
        """基于大模型识别意图
        
        Args:
            text (str): 用户输入文本
            context (Optional[Dict[str, Any]]): 上下文信息
            history (Optional[List[Dict[str, Any]]]): 对话历史
            
        Returns:
            Optional[Intent]: 识别出的意图，如果无法识别则返回None
        """
        # 调用大模型服务进行意图识别
        llm_result = await self.llm_service.recognize_intent(
            text=text,
            context=context,
            message_history=history
        )
        
        # 处理大模型返回结果
        intent_type_str = llm_result.get("data", {}).get("intent", "UNKNOWN")
        confidence = float(llm_result.get("data", {}).get("confidence", 0.7))
        
        # 尝试将字符串转换为枚举类型
        try:
            intent_type = IntentType(intent_type_str)
        except ValueError:
            intent_type = IntentType.UNKNOWN
            
        # 创建意图对象
        intent = Intent(
            type=intent_type,
            confidence=confidence,
            text=text,
            entities={}  # 简化版没有实体信息
        )
        
        return intent 