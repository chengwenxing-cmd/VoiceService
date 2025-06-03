#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图仓储接口模块
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entity.intent import Intent


class IntentRepository(ABC):
    """意图仓储接口"""

    @abstractmethod
    async def save(self, intent: Intent) -> None:
        """保存意图记录

        Args:
            intent (Intent): 意图实体
        """
        pass

    @abstractmethod
    async def find_by_text(self, text: str) -> Optional[Intent]:
        """根据文本查找意图

        Args:
            text (str): 文本内容

        Returns:
            Optional[Intent]: 意图实体，如果不存在则返回None
        """
        pass

    @abstractmethod
    async def find_recent(self, limit: int = 10) -> List[Intent]:
        """查询最近的意图记录

        Args:
            limit (int, optional): 返回记录数量限制. 默认为10.

        Returns:
            List[Intent]: 意图记录列表
        """
        pass
