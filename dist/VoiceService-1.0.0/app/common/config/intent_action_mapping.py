#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图到动作的映射配置
"""

from app.domain.entity.intent import IntentType
from app.domain.entity.action import ActionType

# 意图到动作类型的映射
INTENT_TO_ACTION_MAPPING = {
    # 设备控制
    IntentType.CONTROL_DEVICE_ON: {
        "type": ActionType.DEVICE_CONTROL,
        "operation": "开启"
    },
    IntentType.CONTROL_DEVICE_OFF: {
        "type": ActionType.DEVICE_CONTROL,
        "operation": "关闭"
    },
    
    # 查询
    IntentType.QUERY_WEATHER: {
        "type": ActionType.INFORMATION_QUERY,
        "target": "天气"
    },
    IntentType.QUERY_TIME: {
        "type": ActionType.INFORMATION_QUERY,
        "target": "时间"
    },
    
    # 媒体
    IntentType.PLAY_MUSIC: {
        "type": ActionType.MEDIA_OPERATION,
        "operation": "播放",
        "target": "音乐"
    },
    IntentType.PAUSE_MUSIC: {
        "type": ActionType.MEDIA_OPERATION,
        "operation": "暂停",
        "target": "音乐"
    },
    
    # 录音
    IntentType.STARTRECORDING: {
        "type": ActionType.RECORDING_OPERATION,
        "operation": "开始",
        "target": "录音"
    },
    IntentType.STOPRECORDING: {
        "type": ActionType.RECORDING_OPERATION,
        "operation": "停止",
        "target": "录音"
    },
    
    # 提醒
    IntentType.SET_REMINDER: {
        "type": ActionType.REMINDER_OPERATION,
        "operation": "设置"
    },
    
    # 通用映射
    IntentType.CONTROL_DEVICE: {
        "type": ActionType.DEVICE_CONTROL
    },
    IntentType.QUERY_INFO: {
        "type": ActionType.INFORMATION_QUERY
    },
    IntentType.MEDIA_CONTROL: {
        "type": ActionType.MEDIA_OPERATION
    },
    IntentType.RECORDING_CONTROL: {
        "type": ActionType.RECORDING_OPERATION
    },
    IntentType.REMINDER_SET: {
        "type": ActionType.REMINDER_OPERATION
    },
    IntentType.CHAT: {
        "type": ActionType.CHAT_RESPONSE
    },
    IntentType.UNKNOWN: {
        "type": ActionType.UNKNOWN
    }
} 