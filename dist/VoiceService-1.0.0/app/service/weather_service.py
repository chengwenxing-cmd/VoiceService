#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
天气服务模块
"""

from typing import Dict, Any, Optional

from app.service.base_service import BaseService
from app.adapters.api.weather_api import WeatherAPI

class WeatherService(BaseService):
    """天气服务类，提供天气查询功能"""
    
    def __init__(self, weather_api: Optional[WeatherAPI] = None):
        """初始化天气服务
        
        Args:
            weather_api (Optional[WeatherAPI], optional): 天气API适配器. 默认为None.
        """
        super().__init__("weather_service")
        self.weather_api = weather_api or WeatherAPI()
        self.logger.info("天气服务初始化完成")
    
    async def query_weather(self, city: str, date: Optional[str] = None) -> Dict[str, Any]:
        """查询城市天气
        
        Args:
            city (str): 城市名称
            date (Optional[str], optional): 日期描述，如"今天"、"明天". 默认为None表示今天.
            
        Returns:
            Dict[str, Any]: 天气查询结果
        """
        self.logger.info(f"开始查询天气，城市: {city}, 日期: {date or '今天'}")
        
        try:
            # 确保城市名称有效
            if not city or len(city) < 2:
                self.logger.warning(f"城市名称无效: '{city}'，使用默认城市'北京'")
                city = "北京"
                
            # 清理城市名称，去除可能的干扰字符
            import re
            city = re.sub(r'[^\u4e00-\u9fa5]', '', city)  # 只保留中文字符
            self.logger.info(f"清理后的城市名称: '{city}'")
            
            # 调用天气API获取天气数据
            self.logger.info(f"调用天气API: 城市={city}, 日期={date}")
            weather_data = await self.weather_api.get_weather(city, date)
            
            if not weather_data.get("success", False):
                self.logger.error(f"获取天气数据失败: {weather_data.get('message')}")
                return {
                    "status": "error",
                    "message": f"获取{city}天气信息失败",
                    "error": weather_data.get("message", "未知错误"),
                    "code": 500
                }
            
            # 从天气数据中提取有用信息
            data = weather_data.get("data", {})
            weather = data.get("weather", "未知")
            temperature = data.get("temperature", "未知")
            is_forecast = data.get("is_forecast", False)
            date_info = data.get("date", "今天")
            
            # 构建用户友好的天气消息
            date_desc = "今天" if not date or date in ["今天", "当前", "现在"] else date
            is_mock = data.get("is_mock", False)
            mock_notice = "（模拟数据）" if is_mock else ""
            
            if is_forecast:
                message = f"{city}{date_desc}天气{mock_notice}：{weather}，温度{temperature}°C"
            else:
                message = f"{city}当前天气{mock_notice}：{weather}，温度{temperature}°C"
                
            if "wind_direction" in data and "wind_power" in data:
                message += f"，{data['wind_direction']}风{data['wind_power']}"
                
            if "humidity" in data:
                message += f"，湿度{data['humidity']}"
            
            # 返回结构化的天气查询结果
            return {
                "status": "success",
                "query_type": "weather",
                "message": message,
                "code": 200,
                "data": {
                    "command": "query_weather",
                    "params": {
                        "city": city,
                        "date": date_desc
                    },
                    "result": data
                }
            }
            
        except Exception as e:
            self.logger.error(f"查询天气失败: {str(e)}")
            return {
                "status": "error",
                "message": f"查询{city}天气信息时发生错误",
                "error": str(e),
                "code": 500
            }
