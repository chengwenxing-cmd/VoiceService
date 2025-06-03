#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于规则的意图识别策略
"""

from typing import Dict, Any, List, Optional

from app.domain.strategy.base_strategy import IntentStrategy
from app.domain.entity.intent import Intent, IntentType
from app.common.config.intent_keywords import (
    RECORDING_KEYWORDS, 
    QUESTION_WORDS, 
    SENTIMENT_WORDS
)


class RuleBasedStrategy(IntentStrategy):
    """基于规则的意图识别策略"""
    
    async def recognize(self, text: str, context: Optional[Dict[str, Any]], 
                      history: Optional[List[Dict[str, Any]]]) -> Optional[Intent]:
        """基于规则识别意图
        
        Args:
            text (str): 用户输入文本
            context (Optional[Dict[str, Any]]): 上下文信息
            history (Optional[List[Dict[str, Any]]]): 对话历史
            
        Returns:
            Optional[Intent]: 识别出的意图，如果无法识别则返回None
        """
        # 检查是否是录音相关的意图
        has_recording = any(keyword in text for keyword in RECORDING_KEYWORDS)
        has_question = any(word in text for word in QUESTION_WORDS)
        has_sentiment = any(word in text for word in SENTIMENT_WORDS)
        
        # 复杂的录音相关表达，不应用简单规则
        is_complex_recording_expression = has_recording and (has_question or has_sentiment)
        if is_complex_recording_expression:
            return None
            
        # 简单的录音开始指令
        if has_recording and ("开始" in text or "录" in text) and not "停" in text:
            return Intent(
                type=IntentType.STARTRECORDING, 
                confidence=0.95,
                text=text,
                entities={"operation": "开始", "target": "录音"}
            )
            
        # 简单的录音停止指令
        if has_recording and ("停" in text or "结束" in text or "完成" in text):
            return Intent(
                type=IntentType.STOPRECORDING,
                confidence=0.95,
                text=text,
                entities={"operation": "停止", "target": "录音"}
            )
            
        # 其他简单规则可以在这里添加
        
        # 未匹配到任何规则
        return None 