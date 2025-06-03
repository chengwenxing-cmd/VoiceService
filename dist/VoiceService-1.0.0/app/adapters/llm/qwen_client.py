#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
千问大模型客户端
"""

import json
from typing import Dict, List, Any, Optional
from app.config import settings
from app.common.exception import LLMException
from app.common.logging.logger import log_manager
from app.adapters.prompts import load_prompt

# 创建日志器
logger = log_manager.get_logger("qwen_client")

# 尝试导入dashscope，如果失败则使用模拟实现
try:
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
    logger.info("成功导入dashscope库")
except ImportError:
    logger.warning("无法导入dashscope库，将使用模拟实现")
    DASHSCOPE_AVAILABLE = False
    
    # 创建模拟的Generation类
    class Generation:
        @staticmethod
        def call(model, **kwargs):
            logger.warning("使用模拟的千问大模型实现")
            # 返回模拟的响应
            return {
                "status_code": 200,
                "output": {
                    "text": json.dumps({
                        "intent": "模拟意图",
                        "confidence": 0.95,
                        "action": "模拟动作",
                        "slots": {
                            "mock_slot": "模拟值"
                        }
                    }, ensure_ascii=False)
                }
            }

class QwenClient:
    """千问大模型客户端"""
    
    def __init__(self):
        """初始化千问客户端"""
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.QWEN_MODEL_NAME
        
        if not self.api_key:
            logger.error("未配置DASHSCOPE_API_KEY，无法使用千问大模型服务")
            raise LLMException("未配置DASHSCOPE_API_KEY")
        
        logger.info(f"千问大模型客户端初始化完成，使用模型: {self.model}")
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1500,
        result_format: str = "json"
    ) -> Dict[str, Any]:
        """执行聊天补全请求
        
        Args:
            messages (List[Dict[str, str]]): 消息列表，格式为[{"role": "user", "content": "..."}, ...]
            temperature (float, optional): 温度参数，控制随机性. 默认为0.7.
            max_tokens (int, optional): 最大生成token数. 默认为1500.
            result_format (str, optional): 结果格式，可选json或text. 默认为"json".
            
        Returns:
            Dict[str, Any]: 响应结果
            
        Raises:
            LLMException: 调用大模型失败时抛出
        """
        try:
            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "result_format": result_format,
                "api_key": self.api_key
            }
            
            logger.debug(f"发送千问请求: {messages}")
            
            # 调用API
            response = Generation.call(**request_params)
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"千问API调用失败: {response.code}, {response.message}"
                logger.error(error_msg)
                raise LLMException(error_msg)
            
            # 解析响应
            result = {
                "content": response.output.text,
                "usage": response.usage,
                "request_id": response.request_id
            }
            
            # 如果是JSON格式，尝试解析内容
            if result_format == "json" and result["content"]:
                try:
                    result["content"] = json.loads(result["content"])
                except json.JSONDecodeError:
                    logger.warning("JSON解析失败，返回原始文本")
                    # 构建一个符合预期格式的字典，防止后续处理出错
                    result["content"] = {
                        "success": False,
                        "message": "JSON解析失败",
                        "data": {
                            "intent": "UNKNOWN",
                            "confidence": 0.0,
                            "entities": {},
                            "reply": "抱歉，我遇到了一些技术问题，暂时无法理解您的请求。"
                        }
                    }
            
            logger.debug(f"千问响应成功: {result}")
            return result
            
        except Exception as e:
            error_msg = f"调用千问API异常: {str(e)}"
            logger.error(error_msg)
            raise LLMException(error_msg)
    
    async def intent_recognition(
        self, 
        text: str,
        context: Optional[Dict[str, Any]] = None,
        message_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """识别文本的意图
        
        Args:
            text (str): 需要识别的文本
            context (Optional[Dict[str, Any]], optional): 上下文信息. 默认为None.
            message_history (Optional[List[Dict[str, str]]], optional): 消息历史. 默认为None.
            
        Returns:
            Dict[str, Any]: 意图识别结果
            
        Raises:
            LLMException: 调用大模型失败时抛出
        """
        # 构建提示消息
        system_prompt = self._get_intent_system_prompt()
        user_prompt = self._get_intent_user_prompt(text, context)
        
        # 初始化消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史消息（如果有）
        if message_history and len(message_history) > 0:
            messages.extend(message_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # 调用大模型
            result = await self.chat_completion(
                messages=messages,
                temperature=0.3,  # 降低随机性，提高一致性
                result_format="json"
            )
            
            content = result["content"]
            # 确保content是字典类型
            if not isinstance(content, dict):
                logger.error(f"LLM返回了非字典格式的内容: {content}")
                return {
                    "success": False,
                    "message": "LLM返回了非字典格式的内容",
                    "data": {
                        "intent": "UNKNOWN",
                        "confidence": 0.0,
                        "entities": {},
                        "reply": "抱歉，我遇到了一些技术问题，暂时无法理解您的请求。"
                    }
                }
            
            return content
        except Exception as e:
            logger.error(f"意图识别失败: {str(e)}")
            # 返回一个默认响应，而不是抛出异常
            return {
                "success": False,
                "message": f"意图识别失败: {str(e)}",
                "data": {
                    "intent": "UNKNOWN",
                    "confidence": 0.0,
                    "entities": {},
                    "reply": "抱歉，我遇到了一些技术问题，暂时无法理解您的请求。"
                }
            }
    
    def _get_intent_system_prompt(self) -> str:
        """获取意图识别的系统提示
        
        Returns:
            str: 系统提示文本
        """
        try:
            return load_prompt("system_prompt.txt")
        except FileNotFoundError as e:
            logger.error(f"加载意图识别系统提示模板失败: {str(e)}")
            # 如果文件不存在，返回一个简化版的系统提示
            return "你是一个专业的语音助手意图识别系统。分析用户输入，识别意图类型并返回JSON格式的响应。"
    
    def _get_intent_user_prompt(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """获取意图识别的用户提示
        
        Args:
            text (str): 用户文本
            context (Optional[Dict[str, Any]], optional): 上下文信息. 默认为None.
            
        Returns:
            str: 用户提示文本
        """
        try:
            # 加载提示模板
            template = load_prompt("user_prompt.txt")
            
            # 准备上下文信息
            context_info = ""
            if context and isinstance(context, dict) and context:
                context_str = json.dumps(context, ensure_ascii=False, indent=2)
                context_info = f"上下文信息：\n{context_str}"
            
            # 填充模板
            return template.format(text=text, context_info=context_info)
        except FileNotFoundError as e:
            logger.error(f"加载意图识别用户提示模板失败: {str(e)}")
            # 如果文件不存在，回退到原来的提示格式
            prompt = f"请分析以下文本，识别其中的意图和实体，并生成相应的动作指令：\n\n{text}"
            
            if context and isinstance(context, dict) and context:
                context_str = json.dumps(context, ensure_ascii=False, indent=2)
                prompt += f"\n\n上下文信息：\n{context_str}"
            
            return prompt
