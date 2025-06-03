#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图识别相关异常
"""

from app.common.exception import AppException


class IntentRecognitionError(AppException):
    """意图识别错误基类"""
    pass


class ModelCallError(IntentRecognitionError):
    """大模型调用错误"""
    pass


class IntentParsingError(IntentRecognitionError):
    """意图解析错误"""
    pass


class ActionGenerationError(IntentRecognitionError):
    """动作生成错误"""
    pass


class ResultGenerationError(IntentRecognitionError):
    """结果生成错误"""
    pass 