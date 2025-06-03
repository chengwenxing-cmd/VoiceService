#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于缓存的意图识别策略
"""

from typing import Dict, Any, List, Optional

from app.domain.strategy.base_strategy import IntentStrategy
from app.domain.entity.intent import Intent
from app.domain.repository.intent_repository import IntentRepository


class CacheBasedStrategy(IntentStrategy):
    """基于缓存的意图识别策略"""
    
    def __init__(self, intent_repository: IntentRepository):
        """初始化
        
        Args:
            intent_repository (IntentRepository): 意图仓储
        """
        self.intent_repository = intent_repository
    
    async def recognize(self, text: str, context: Optional[Dict[str, Any]], 
                      history: Optional[List[Dict[str, Any]]]) -> Optional[Intent]:
        """基于缓存识别意图
        
        Args:
            text (str): 用户输入文本
            context (Optional[Dict[str, Any]]): 上下文信息
            history (Optional[List[Dict[str, Any]]]): 对话历史
            
        Returns:
            Optional[Intent]: 识别出的意图，如果无法识别则返回None
        """
        # 查询缓存
        cached_intent = await self.intent_repository.find_by_text(text)
        
        # 如果没有缓存结果或置信度不够高，返回None
        if not cached_intent or cached_intent.confidence < 0.9:
            return None
            
        # 如果对话历史过长，可能上下文已经变化，不使用缓存
        if history and len(history) > 2:
            # 未来可以实现更复杂的上下文相似度计算
            return None
            
        return cached_intent 