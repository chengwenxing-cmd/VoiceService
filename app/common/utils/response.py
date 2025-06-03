#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API响应工具模块
"""


class ResponseUtil:
    """API响应工具类"""

    @staticmethod
    def success(data=None, message="Success"):
        """成功响应

        Args:
            data: 响应数据
            message (str): 响应消息

        Returns:
            dict: 响应对象
        """
        return {
            "success": True,
            "message": message,
            "data": data or {}
        }

    @staticmethod
    def error(message="Error", code=500, data=None):
        """错误响应

        Args:
            message (str): 错误消息
            code (int): 错误代码
            data: 错误数据

        Returns:
            dict: 响应对象
        """
        return {
            "success": False,
            "message": message,
            "code": code,
            "data": data or {}
        }
