#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于规则的意图识别策略
"""

from typing import Dict, Any, List, Optional
import re

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
        
        # 天气查询意图识别
        weather_patterns = [
            r'(今天|明天|后天|周[一二三四五六日天]|星期[一二三四五六日天]|[\u4e00-\u9fa5]{2,6})(的)?天气(怎么样|如何|预报|情况)?',
            r'天气(怎么样|如何|预报|情况)?',
            r'(查询|查看|知道)(今天|明天|后天|周[一二三四五六日天]|星期[一二三四五六日天]|[\u4e00-\u9fa5]{2,6})?(的)?天气'
        ]
        
        # 检查文本是否匹配天气查询模式
        for pattern in weather_patterns:
            if re.search(pattern, text):
                # 尝试提取城市和日期
                entities = {}
                
                # 尝试提取城市
                city_match = re.search(r'([\u4e00-\u9fa5]{2,6})(的天气|天气)', text)
                if city_match:
                    potential_city = city_match.group(1)
                    if potential_city not in ["今天", "明天", "后天", "当前", "今日", "明日"]:
                        entities["city"] = potential_city
                
                # 尝试提取日期
                date_patterns = {
                    "今天|今日|当前": "今天",
                    "明天|明日": "明天",
                    "后天": "后天",
                    "大后天": "大后天",
                    "周一|星期一": "周一",
                    "周二|星期二": "周二",
                    "周三|星期三": "周三",
                    "周四|星期四": "周四",
                    "周五|星期五": "周五",
                    "周六|星期六": "周六",
                    "周日|周天|星期日|星期天": "周日"
                }
                
                for pattern, date_value in date_patterns.items():
                    if re.search(pattern, text):
                        entities["date"] = date_value
                        break
                
                return Intent(
                    type=IntentType.QUERY_WEATHER,
                    confidence=0.9,
                    text=text,
                    entities=entities
                )
            
        # 其他简单规则可以在这里添加
        
        # 未匹配到任何规则
        return None 