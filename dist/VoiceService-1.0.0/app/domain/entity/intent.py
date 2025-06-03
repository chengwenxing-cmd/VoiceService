#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图实体模块
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any


class IntentType(str, Enum):
    """意图类型枚举"""
    CONTROL_DEVICE = "control_device"  # 控制设备
    QUERY_INFO = "query_info"          # 查询信息
    MEDIA_CONTROL = "media_control"    # 媒体控制
    RECORDING_CONTROL = "recording_control"  # 录音控制
    REMINDER_SET = "reminder_set"      # 设置提醒
    CHAT = "chat"                      # 闲聊
    UNKNOWN = "unknown"                # 未知意图
    
    # 新增具体意图类型
    CONTROL_DEVICE_ON = "CONTROL_DEVICE_ON"    # 打开设备
    CONTROL_DEVICE_OFF = "CONTROL_DEVICE_OFF"  # 关闭设备
    QUERY_WEATHER = "QUERY_WEATHER"            # 查询天气
    QUERY_TIME = "QUERY_TIME"                  # 查询时间
    PLAY_MUSIC = "PLAY_MUSIC"                  # 播放音乐
    PAUSE_MUSIC = "PAUSE_MUSIC"                # 暂停音乐
    STARTRECORDING = "STARTRECORDING"          # 开始录音
    STOPRECORDING = "STOPRECORDING"            # 停止录音
    SET_REMINDER = "SET_REMINDER"              # 设置提醒


class Intent(BaseModel):
    """意图实体类"""
    
    type: IntentType = Field(
        default=IntentType.UNKNOWN,
        description="意图类型"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="意图置信度，范围0-1"
    )
    text: str = Field(
        default="",
        description="原始文本"
    )
    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="识别出的实体信息"
    )

    class Config:
        """Pydantic配置"""
        frozen = True  # 不可变对象
