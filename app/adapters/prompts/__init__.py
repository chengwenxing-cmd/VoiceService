#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提示模板模块
"""

from pathlib import Path

def load_prompt(filename: str, category: str = None) -> str:
    """加载提示模板文件
    
    Args:
        filename (str): 提示模板文件名
        category (str, optional): 提示类别子目录. 默认为None，表示直接从prompts目录加载.
        
    Returns:
        str: 提示模板内容
    """
    prompt_dir = Path(__file__).parent
    
    if category:
        prompt_file = prompt_dir / category / filename
    else:
        prompt_file = prompt_dir / filename
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"提示模板文件不存在: {prompt_file}")
    
    return prompt_file.read_text(encoding="utf-8")
