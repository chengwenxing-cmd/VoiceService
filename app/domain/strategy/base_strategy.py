#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图识别策略基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from app.domain.entity.intent import Intent


class IntentStrategy(ABC):
    """意图识别策略基类"""
    
    @abstractmethod
    async def recognize(self, text: str, context: Optional[Dict[str, Any]], 
                      history: Optional[List[Dict[str, Any]]]) -> Optional[Intent]:
        """识别意图
        
        Args:
            text (str): 用户输入文本
            context (Optional[Dict[str, Any]]): 上下文信息
            history (Optional[List[Dict[str, Any]]]): 对话历史
            
        Returns:
            Optional[Intent]: 识别出的意图，如果无法识别则返回None
        """
        pass 