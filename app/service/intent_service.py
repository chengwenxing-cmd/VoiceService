#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图识别服务模块
"""

from typing import Dict, Any, Optional, List, Pattern, Match
import re
from app.service.base_service import BaseService
from app.service.llm_service import LLMService
from app.service.dialogue_context_service import dialogue_context_service
from app.service.weather_service import WeatherService
from app.domain.entity.intent import Intent, IntentType
from app.domain.entity.action import Action, ActionType
from app.domain.repository.intent_repository import IntentRepository
from app.adapters.repository.postgres_repository import PostgresIntentRepository
from app.domain.value_object.request_response import IntentRecognizeResponse
from app.common.exception import AppException
from app.common.exception.intent_exceptions import (
    IntentRecognitionError, 
    ModelCallError, 
    ActionGenerationError,
    ResultGenerationError
)

# 导入策略
from app.domain.strategy.base_strategy import IntentStrategy
from app.domain.strategy.cache_strategy import CacheBasedStrategy
from app.domain.strategy.rule_strategy import RuleBasedStrategy
from app.domain.strategy.llm_strategy import LLMBasedStrategy

# 导入配置
from app.common.config.intent_action_mapping import INTENT_TO_ACTION_MAPPING


class IntentService(BaseService):
    """意图识别服务"""
    
    def __init__(self, 
                llm_service: Optional[LLMService] = None,
                intent_repository: Optional[IntentRepository] = None,
                weather_service: Optional[WeatherService] = None):
        """初始化意图识别服务
        
        Args:
            llm_service (Optional[LLMService], optional): 大模型服务. 默认为None.
            intent_repository (Optional[IntentRepository], optional): 意图仓储. 默认为None.
            weather_service (Optional[WeatherService], optional): 天气服务. 默认为None.
        """
        super().__init__("intent_service")
        
        # 初始化依赖服务和仓储
        self.llm_service = llm_service or LLMService()
        self.intent_repository = intent_repository or PostgresIntentRepository()
        self.weather_service = weather_service or WeatherService()
        
        # 初始化策略
        self.strategies: List[IntentStrategy] = [
            CacheBasedStrategy(self.intent_repository),
            RuleBasedStrategy(),
            LLMBasedStrategy(self.llm_service)
        ]
        
        self.logger.info("意图识别服务初始化成功")
    
    async def recognize_intent(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None,
        session_id: str = "default"
    ) -> IntentRecognizeResponse:
        """识别文本意图并生成动作
        
        Args:
            text (str): 待识别的文本
            context (Optional[Dict[str, Any]], optional): 上下文信息. 默认为None.
            session_id (str, optional): 会话ID，用于跟踪对话上下文. 默认为"default".
            
        Returns:
            IntentRecognizeResponse: 意图识别响应
            
        Raises:
            AppException: 处理失败时抛出
        """
        try:
            self.logger.info(f"开始处理意图识别请求，文本: {text}, 会话ID: {session_id}")
            
            # 1. 准备上下文
            await self._prepare_context(text, session_id)
            
            # 2. 识别意图
            intent = await self._identify_intent(text, context, session_id)
            
            # 3. 生成动作
            action = await self._generate_action(intent)
            
            # 4. 生成结果
            result = await self._generate_result(intent, action, session_id)
            
            # 5. 保存意图
            await self._save_intent(intent)
            
            self.logger.info(f"意图识别完成，类型: {intent.type}，动作类型: {action.type}")
            return IntentRecognizeResponse(intent=intent, action=action, result=result)
            
        except IntentRecognitionError as e:
            error_msg = f"意图识别处理失败: {str(e)}"
            self.logger.error(error_msg)
            raise AppException(error_msg)
        except Exception as e:
            error_msg = f"意图识别发生未预期错误: {str(e)}"
            self.logger.error(error_msg)
            raise AppException(error_msg)
    
    async def _prepare_context(self, text: str, session_id: str) -> None:
        """准备上下文
        
        Args:
            text (str): 用户输入文本
            session_id (str): 会话ID
        """
        # 将用户消息添加到对话上下文
        dialogue_context_service.add_user_message(session_id, text)
    
    async def _identify_intent(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]], 
        session_id: str
    ) -> Intent:
        """识别意图
        
        Args:
            text (str): 用户输入文本
            context (Optional[Dict[str, Any]]): 上下文信息
            session_id (str): 会话ID
            
        Returns:
            Intent: 识别出的意图
            
        Raises:
            ModelCallError: 调用模型失败时抛出
        """
        try:
            # 获取历史消息
            message_history = dialogue_context_service.get_history(session_id)
            
            # 依次尝试每个策略
            for strategy in self.strategies:
                intent = await strategy.recognize(text, context, message_history)
                if intent:
                    self.logger.info(f"使用策略 {strategy.__class__.__name__} 识别出意图: {intent.type}")
                    return intent
            
            # 所有策略都失败，返回未知意图
            self.logger.warning("所有策略都未能识别出意图，返回UNKNOWN")
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.1,
                text=text,
                entities={}
            )
        except Exception as e:
            self.logger.error(f"识别意图失败: {str(e)}")
            raise ModelCallError(f"识别意图失败: {str(e)}")
    
    async def _generate_action(self, intent: Intent) -> Action:
        """根据意图生成动作
        
        Args:
            intent (Intent): 意图
            
        Returns:
            Action: 生成的动作
            
        Raises:
            ActionGenerationError: 生成动作失败时抛出
        """
        try:
            # 获取动作配置
            action_config = INTENT_TO_ACTION_MAPPING.get(intent.type, {"type": ActionType.UNKNOWN})
            
            # 从实体中提取相关信息
            entities = intent.entities
            target = action_config.get("target", entities.get("target", ""))
            operation = action_config.get("operation", entities.get("operation", ""))
            parameters = {k: v for k, v in entities.items() 
                        if k not in ["target", "operation"]}
            
            # 创建动作实体
            return Action(
                type=action_config["type"],
                target=target,
                operation=operation,
                parameters=parameters
            )
        except Exception as e:
            self.logger.error(f"生成动作失败: {str(e)}")
            raise ActionGenerationError(f"生成动作失败: {str(e)}")
    
    async def _generate_result(
        self, 
        intent: Intent, 
        action: Action,
        session_id: str
    ) -> Dict[str, Any]:
        """生成结果
        
        Args:
            intent (Intent): 意图
            action (Action): 动作
            session_id (str): 会话ID
            
        Returns:
            Dict[str, Any]: 结果数据
            
        Raises:
            ResultGenerationError: 生成结果失败时抛出
        """
        try:
            result = {}
            
            # 根据意图类型生成不同的结果
            if intent.type == IntentType.UNKNOWN:
                # 使用大模型生成回复，而不是硬编码
                try:
                    # 获取LLM生成的回复
                    llm_response = await self.llm_service.recognize_intent(intent.text, context={
                        "session_id": session_id,
                        "intent_type": "UNKNOWN"
                    })
                    
                    # 从LLM响应中提取回复文本
                    if llm_response and "data" in llm_response and "reply" in llm_response["data"]:
                        message = llm_response["data"]["reply"]
                    else:
                        # 如果LLM没有返回有效回复，使用更友好的默认回复
                        message = "我可能没有完全理解您的意思，能否请您换种方式表达？"
                        
                    result = {
                        "status": "unknown_intent",
                        "message": message,
                        "code": 200,
                        "data": {
                            "command": "chat_reply",
                            "params": {}
                        }
                    }
                    dialogue_context_service.add_assistant_message(session_id, message)
                except Exception as e:
                    # 如果LLM调用失败，记录错误并使用备用回复
                    self.logger.error(f"使用LLM生成未知意图回复失败: {str(e)}")
                    message = "我可能没有完全理解您的意思，能否请您换种方式表达？"
                    result = {
                        "status": "unknown_intent",
                        "message": message,
                        "code": 200,
                        "data": {
                            "command": "chat_reply",
                            "params": {}
                        }
                    }
                    dialogue_context_service.add_assistant_message(session_id, message)
            elif intent.type == IntentType.CHAT:
                # 闲聊意图，提供对话回复
                message = "很高兴与您聊天。"
                result = {
                    "status": "chat",
                    "message": message,
                    "code": 200,
                    "data": {
                        "command": "chat_reply",
                        "params": {}
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, message)
            # 录音相关意图
            elif intent.type == IntentType.STARTRECORDING:
                result = {
                    "status": "started",
                    "recording_id": "rec_" + str(hash(intent.text) % 10000),
                    "message": "录音已开始",
                    "code": 200,
                    "data": {
                        "command": "start_recording",
                        "params": {}
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, "录音已开始")
            elif intent.type == IntentType.STOPRECORDING:
                result = {
                    "status": "stopped",
                    "recording_id": "rec_" + str(hash(intent.text) % 10000),
                    "duration": 120,  # 模拟录音时长(秒)
                    "message": "录音已停止",
                    "code": 200,
                    "data": {
                        "command": "stop_recording",
                        "params": {}
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, "录音已停止")
            # 媒体相关意图
            elif intent.type == IntentType.PLAY_MUSIC:
                result = {
                    "status": "playing",
                    "media_type": "music",
                    "message": "正在播放音乐",
                    "code": 200,
                    "data": {
                        "command": "play_media",
                        "params": {
                            "type": "music"
                        }
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, "正在播放音乐")
            elif intent.type == IntentType.PAUSE_MUSIC:
                result = {
                    "status": "paused",
                    "media_type": "music",
                    "message": "音乐已暂停",
                    "code": 200,
                    "data": {
                        "command": "pause_media",
                        "params": {
                            "type": "music"
                        }
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, "音乐已暂停")
            # 设备控制意图
            elif intent.type in [IntentType.CONTROL_DEVICE_ON, IntentType.CONTROL_DEVICE_OFF]:
                status = "on" if intent.type == IntentType.CONTROL_DEVICE_ON else "off"
                target = action.target or "设备"
                message = f"{target}已{action.operation}"
                result = {
                    "status": status,
                    "device": target,
                    "message": message,
                    "code": 200,
                    "data": {
                        "command": f"device_{status}",
                        "params": {
                            "device": target
                        }
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, message)
            # 查询意图
            elif intent.type == IntentType.QUERY_WEATHER:
                # 从意图实体中提取城市和日期信息
                city = intent.entities.get("city")
                date = intent.entities.get("date")
                
                # 记录提取的实体信息
                self.logger.info(f"处理天气查询意图，原始文本: '{intent.text}'")
                self.logger.info(f"提取的实体: 城市='{city}', 日期='{date}'")
                
                # 如果没有提取到城市，使用正则表达式尝试从文本中提取
                if not city:
                    # 预定义的城市列表，包括主要城市和省会城市
                    common_cities = [
                        "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "西安", "成都", "重庆", 
                        "天津", "长沙", "苏州", "厦门", "哈尔滨", "大连", "青岛", "济南", "郑州", "长春",
                        "沈阳", "南宁", "昆明", "贵阳", "太原", "石家庄", "乌鲁木齐", "兰州", "西宁", "银川",
                        "呼和浩特", "拉萨", "南昌", "合肥", "福州", "台北", "海口", "三亚"
                    ]
                    
                    # 1. 直接文本匹配
                    for potential_city in common_cities:
                        if potential_city in intent.text:
                            city = potential_city
                            self.logger.info(f"从文本中匹配到城市: {city}")
                            break
                    
                    # 2. 如果仍未找到，使用正则表达式尝试匹配更复杂的模式
                    if not city:
                        # 匹配"XX的天气"或"XX天气"模式
                        city_pattern = re.compile(r'([\u4e00-\u9fa5]{2,6})(的天气|天气)')
                        match = city_pattern.search(intent.text)
                        if match:
                            potential_city = match.group(1)
                            # 验证提取的是否为有效城市名
                            if len(potential_city) >= 2 and potential_city not in ["今天", "明天", "后天", "当前", "今日", "明日"]:
                                city = potential_city
                                self.logger.info(f"通过正则表达式匹配到城市: {city}")
                
                # 如果仍未找到城市，使用默认值
                if not city:
                    city = "北京"  # 默认城市
                    self.logger.info(f"未找到城市信息，使用默认城市: {city}")
                
                # 如果没有提取到日期，尝试从文本中提取
                if not date:
                    date_patterns = {
                        "今天|今日|当前|现在": "今天",
                        "明天|明日": "明天",
                        "后天": "后天",
                        "大后天": "大后天",
                        "周一|星期一": "周一",
                        "周二|星期二": "周二",
                        "周三|星期三": "周三",
                        "周四|星期四": "周四",
                        "周五|星期五": "周五",
                        "周六|星期六": "周六",
                        "周日|周天|星期日|星期天": "周日"
                    }
                    
                    for pattern, date_value in date_patterns.items():
                        if re.search(pattern, intent.text):
                            date = date_value
                            self.logger.info(f"从文本中匹配到日期: {date}")
                            break
                
                # 调用天气服务获取天气信息
                self.logger.info(f"调用天气服务查询天气: 城市={city}, 日期={date}")
                weather_result = await self.weather_service.query_weather(city, date)
                
                # 获取天气消息
                message = weather_result.get("message", f"获取{city}天气信息失败")
                self.logger.info(f"天气查询结果: {message}")
                
                # 构建结果
                result = weather_result
                
                # 将天气信息添加到对话上下文
                dialogue_context_service.add_assistant_message(session_id, message)
            elif intent.type == IntentType.QUERY_TIME:
                query_type = "time"
                result = {
                    "status": "success",
                    "query_type": query_type,
                    "message": "查询成功",
                    "code": 200,
                    "data": {
                        "command": f"query_{query_type}",
                        "params": {},
                        "result": "模拟查询结果"
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, "查询成功")
            # 通用结果
            else:
                message = f"已执行{action.type.value}操作"
                result = {
                    "status": "success",
                    "action_type": action.type.value,
                    "target": action.target or "",
                    "operation": action.operation or "",
                    "message": message,
                    "code": 200,
                    "data": {
                        "command": "generic_action",
                        "params": {}
                    }
                }
                dialogue_context_service.add_assistant_message(session_id, message)
            
            return result
            
        except Exception as e:
            self.logger.error(f"生成结果数据失败: {str(e)}")
            raise ResultGenerationError(f"生成结果数据失败: {str(e)}")
    
    async def _save_intent(self, intent: Intent) -> None:
        """保存意图
        
        Args:
            intent (Intent): 要保存的意图
        """
        if intent.type != IntentType.UNKNOWN and intent.confidence > 0.7:
            await self.intent_repository.save(intent)
