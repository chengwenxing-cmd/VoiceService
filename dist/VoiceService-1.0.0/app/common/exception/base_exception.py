#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定义异常基类模块
"""


class AppException(Exception):
    """应用程序异常基类"""

    def __init__(self, message="应用程序错误", code=500):
        """初始化异常
        
        Args:
            message (str): 错误消息
            code (int): 错误代码
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResourceNotFoundException(AppException):
    """资源未找到异常"""

    def __init__(self, message="请求的资源不存在"):
        super().__init__(message=message, code=404)


class ValidationException(AppException):
    """数据验证异常"""

    def __init__(self, message="数据验证失败"):
        super().__init__(message=message, code=400)


class AuthenticationException(AppException):
    """认证异常"""

    def __init__(self, message="认证失败"):
        super().__init__(message=message, code=401)


class LLMException(AppException):
    """大模型调用异常"""

    def __init__(self, message="大模型调用失败"):
        super().__init__(message=message, code=500)
