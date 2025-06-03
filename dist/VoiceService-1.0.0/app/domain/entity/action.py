#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
动作实体模块
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ActionType(str, Enum):
    """动作类型枚举"""
    DEVICE_CONTROL = "device_control"          # 设备控制
    INFORMATION_QUERY = "information_query"    # 信息查询
    MEDIA_OPERATION = "media_operation"        # 媒体操作
    RECORDING_OPERATION = "recording_operation"  # 录音操作
    REMINDER_OPERATION = "reminder_operation"  # 提醒操作
    CHAT_RESPONSE = "chat_response"            # 聊天回复
    UNKNOWN = "unknown"                        # 未知


class Action(BaseModel):
    """动作实体类"""
    type: ActionType
    target: Optional[str] = None
    operation: Optional[str] = None
    parameters: Dict[str, Any] = {}
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "type": self.type.value,
            "target": self.target,
            "operation": self.operation,
            "parameters": self.parameters,
            "message": self.message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """从字典创建实例
        
        Args:
            data (Dict[str, Any]): 字典数据
            
        Returns:
            Action: 动作实例
        """
        # 确保类型是ActionType枚举
        if "type" in data and isinstance(data["type"], str):
            try:
                data["type"] = ActionType(data["type"])
            except ValueError:
                data["type"] = ActionType.UNKNOWN
                
        return cls(**data)
