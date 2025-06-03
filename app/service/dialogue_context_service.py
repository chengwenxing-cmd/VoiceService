#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
对话上下文管理服务
"""

from typing import Dict, List, Any, Optional
import time
from app.common.logging.logger import log_manager

# 创建日志器
logger = log_manager.get_logger("dialogue_context")

class DialogueContext:
    """对话上下文类"""
    
    def __init__(self, session_id: str, max_history: int = 5, ttl: int = 1800):
        """初始化对话上下文
        
        Args:
            session_id (str): 会话ID
            max_history (int, optional): 最大历史记录数. 默认为5.
            ttl (int, optional): 会话超时时间(秒). 默认为1800 (30分钟).
        """
        self.session_id = session_id
        self.max_history = max_history
        self.ttl = ttl
        self.history: List[Dict[str, Any]] = []
        self.last_updated = time.time()
        self.metadata: Dict[str, Any] = {}
    
    def add_user_message(self, text: str) -> None:
        """添加用户消息
        
        Args:
            text (str): 用户消息文本
        """
        self.history.append({
            "role": "user",
            "content": text,
            "timestamp": time.time()
        })
        self._trim_history()
        self.last_updated = time.time()
    
    def add_assistant_message(self, text: str) -> None:
        """添加助手消息
        
        Args:
            text (str): 助手消息文本
        """
        self.history.append({
            "role": "assistant",
            "content": text,
            "timestamp": time.time()
        })
        self._trim_history()
        self.last_updated = time.time()
    
    def _trim_history(self) -> None:
        """裁剪历史记录，确保不超过最大长度"""
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def is_expired(self) -> bool:
        """检查会话是否已过期
        
        Returns:
            bool: 如果会话已过期，返回True
        """
        return (time.time() - self.last_updated) > self.ttl
    
    def get_formatted_history(self) -> List[Dict[str, str]]:
        """获取格式化的历史记录，用于发送给大模型
        
        Returns:
            List[Dict[str, str]]: 格式化的历史记录
        """
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.history]
    
    def clear(self) -> None:
        """清空对话历史"""
        self.history = []
        self.last_updated = time.time()


class DialogueContextService:
    """对话上下文管理服务"""
    
    def __init__(self, max_contexts: int = 1000):
        """初始化对话上下文管理服务
        
        Args:
            max_contexts (int, optional): 最大上下文数量. 默认为1000.
        """
        self.contexts: Dict[str, DialogueContext] = {}
        self.max_contexts = max_contexts
        self.logger = logger
        self.logger.info("对话上下文管理服务初始化成功")
    
    def get_context(self, session_id: str) -> DialogueContext:
        """获取或创建对话上下文
        
        Args:
            session_id (str): 会话ID
            
        Returns:
            DialogueContext: 对话上下文
        """
        # 清理过期的上下文
        self._cleanup_expired_contexts()
        
        # 如果上下文不存在，创建新的
        if session_id not in self.contexts:
            self.logger.info(f"为会话 {session_id} 创建新的对话上下文")
            self.contexts[session_id] = DialogueContext(session_id)
            
            # 如果上下文数量超过限制，移除最旧的
            if len(self.contexts) > self.max_contexts:
                oldest_session_id = min(
                    self.contexts.keys(),
                    key=lambda sid: self.contexts[sid].last_updated
                )
                self.logger.info(f"上下文数量超过限制，移除最旧的会话 {oldest_session_id}")
                del self.contexts[oldest_session_id]
        
        return self.contexts[session_id]
    
    def add_user_message(self, session_id: str, text: str) -> None:
        """添加用户消息
        
        Args:
            session_id (str): 会话ID
            text (str): 用户消息文本
        """
        context = self.get_context(session_id)
        context.add_user_message(text)
    
    def add_assistant_message(self, session_id: str, text: str) -> None:
        """添加助手消息
        
        Args:
            session_id (str): 会话ID
            text (str): 助手消息文本
        """
        context = self.get_context(session_id)
        context.add_assistant_message(text)
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取对话历史
        
        Args:
            session_id (str): 会话ID
            
        Returns:
            List[Dict[str, str]]: 对话历史
        """
        context = self.get_context(session_id)
        return context.get_formatted_history()
    
    def clear_context(self, session_id: str) -> None:
        """清空对话上下文
        
        Args:
            session_id (str): 会话ID
        """
        if session_id in self.contexts:
            self.logger.info(f"清空会话 {session_id} 的对话上下文")
            self.contexts[session_id].clear()
    
    def delete_context(self, session_id: str) -> None:
        """删除对话上下文
        
        Args:
            session_id (str): 会话ID
        """
        if session_id in self.contexts:
            self.logger.info(f"删除会话 {session_id} 的对话上下文")
            del self.contexts[session_id]
    
    def _cleanup_expired_contexts(self) -> None:
        """清理过期的上下文"""
        expired_sessions = [
            session_id for session_id, context in self.contexts.items()
            if context.is_expired()
        ]
        
        for session_id in expired_sessions:
            self.logger.info(f"会话 {session_id} 已过期，移除上下文")
            del self.contexts[session_id]

# 创建全局服务实例
dialogue_context_service = DialogueContextService() 