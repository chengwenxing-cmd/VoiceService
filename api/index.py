#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vercel Serverless Function入口点
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入FastAPI应用实例
from app.main import app

# 导出给Vercel使用的ASGI应用
app = app 