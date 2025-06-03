#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
天气API适配器模块，使用高德地图API
"""

import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.config import settings
from app.common.logging.logger import log_manager

# 创建日志器
logger = log_manager.get_logger("weather_api")

class WeatherAPI:
    """天气API适配器，使用高德地图API"""
    
    def __init__(self):
        """初始化天气API适配器"""
        self.api_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        self.geo_url = "https://restapi.amap.com/v3/geocode/geo"
        
        # 缓存常用城市编码，避免重复请求
        self.city_code_cache = {
            "北京": "110000",
            "上海": "310000",
            "广州": "440100",
            "深圳": "440300",
            "杭州": "330100",
            "南京": "320100",
            "武汉": "420100",
            "西安": "610100",
            "成都": "510100",
            "重庆": "500000",
            "天津": "120000",
            "长沙": "430100",
            "苏州": "320500",
            "厦门": "350200"
        }
        
        if not self.api_key:
            logger.warning("未配置AMAP_API_KEY，将使用模拟天气数据")
        else:
            logger.info("高德地图天气API适配器初始化完成")
    
    async def get_weather(self, city: str, date: Optional[str] = None) -> Dict[str, Any]:
        """获取城市天气信息
        
        Args:
            city (str): 城市名称，如"西安"、"北京"
            date (Optional[str], optional): 日期描述，如"今天"、"明天". 默认为None表示今天.
        
        Returns:
            Dict[str, Any]: 天气信息
        """
        try:
            # 解析日期
            target_date = self._parse_date(date)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # 判断是否是预报还是实时
            is_forecast = target_date.date() != datetime.now().date()
            
            if not self.api_key:
                logger.warning("未配置高德地图API密钥，使用模拟数据")
                return self._get_mock_weather(city, date_str, is_forecast)
            
            # 获取城市编码
            city_code = await self._get_city_adcode(city)
            if not city_code:
                logger.error(f"无法获取城市 {city} 的编码，使用模拟数据")
                return self._get_mock_weather(city, date_str, is_forecast)
            
            logger.info(f"查询 {city}({city_code}) 的{'天气预报' if is_forecast else '实时天气'}")
            
            # 构建请求参数
            params = {
                "key": self.api_key,
                "city": city_code,
                "extensions": "all" if is_forecast else "base",
                "output": "JSON"
            }
            
            # 发送请求，带重试机制
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.base_url, params=params, timeout=10) as response:
                            if response.status != 200:
                                logger.error(f"天气API请求失败 (尝试 {retry_count+1}/{max_retries}): HTTP {response.status}")
                                retry_count += 1
                                if retry_count >= max_retries:
                                    return self._get_error_response(f"API请求失败: HTTP {response.status}")
                                await asyncio.sleep(1)  # 等待1秒后重试
                                continue
                            
                            data = await response.json()
                            
                            # 检查API返回状态
                            if data.get("status") != "1":
                                error_info = data.get("info", "未知错误")
                                logger.error(f"天气API返回错误: {error_info}")
                                return self._get_error_response(error_info)
                            
                            # 记录原始响应
                            logger.debug(f"高德天气API响应: {data}")
                            
                            # 处理结果
                            if is_forecast:
                                return self._process_forecast(data, city, target_date)
                            else:
                                return self._process_live_weather(data, city)
                    
                except aiohttp.ClientError as e:
                    logger.error(f"天气API请求异常 (尝试 {retry_count+1}/{max_retries}): {str(e)}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        return self._get_error_response(f"API请求异常: {str(e)}")
                    await asyncio.sleep(1)  # 等待1秒后重试
                    
        except Exception as e:
            logger.error(f"获取天气信息失败: {str(e)}")
            return self._get_error_response(f"获取天气信息失败: {str(e)}")
    
    async def _get_city_adcode(self, city_name: str) -> Optional[str]:
        """获取城市编码
        
        Args:
            city_name (str): 城市名称
            
        Returns:
            Optional[str]: 城市编码，失败时返回None
        """
        # 清理城市名称，只保留中文字符
        import re
        city_name = re.sub(r'[^\u4e00-\u9fa5]', '', city_name).strip()
        if not city_name:
            logger.error("城市名称无效")
            return None
        
        # 检查缓存
        if city_name in self.city_code_cache:
            logger.info(f"城市 {city_name} 的编码从缓存获取: {self.city_code_cache[city_name]}")
            return self.city_code_cache[city_name]
        
        # 如果没有API密钥，无法查询城市编码
        if not self.api_key:
            logger.warning(f"未配置API密钥，无法查询城市 {city_name} 的编码")
            return city_name
        
        # 调用地理编码API
        try:
            params = {
                "key": self.api_key,
                "address": city_name,
                "output": "JSON"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.geo_url, params=params, timeout=10) as response:
                    if response.status != 200:
                        logger.error(f"地理编码API请求失败: HTTP {response.status}")
                        return None
                    
                    data = await response.json()
                    logger.debug(f"地理编码API响应: {data}")
                    
                    # 检查API返回状态
                    if data.get("status") != "1" or not data.get("geocodes"):
                        logger.error(f"地理编码API返回错误: {data.get('info', '未知错误')}")
                        return None
                    
                    # 提取城市编码
                    adcode = data["geocodes"][0]["adcode"]
                    
                    # 更新缓存
                    self.city_code_cache[city_name] = adcode
                    logger.info(f"城市 {city_name} 的编码为 {adcode}，已添加到缓存")
                    
                    return adcode
                    
        except Exception as e:
            logger.error(f"获取城市编码失败: {str(e)}")
            return None
    
    def _parse_date(self, date_desc: Optional[str]) -> datetime:
        """解析日期描述
        
        Args:
            date_desc (Optional[str]): 日期描述，如"今天"、"明天"、"后天"
            
        Returns:
            datetime: 日期对象
        """
        today = datetime.now()
        logger.info(f"开始解析日期描述: '{date_desc}', 当前日期时间: {today.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not date_desc or date_desc in ["今天", "当前", "现在"]:
            logger.info(f"识别为今天: {today.strftime('%Y-%m-%d')}")
            return today
        elif date_desc in ["明天", "明日"]:
            tomorrow = today + timedelta(days=1)
            logger.info(f"识别为明天: {tomorrow.strftime('%Y-%m-%d')}")
            return tomorrow
        elif date_desc in ["后天"]:
            day_after_tomorrow = today + timedelta(days=2)
            logger.info(f"识别为后天: {day_after_tomorrow.strftime('%Y-%m-%d')}")
            return day_after_tomorrow
        elif date_desc in ["大后天"]:
            three_days_later = today + timedelta(days=3)
            logger.info(f"识别为大后天: {three_days_later.strftime('%Y-%m-%d')}")
            return three_days_later
        
        # 尝试解析具体日期，如果失败则返回今天
        try:
            # 处理"周x"或"星期x"格式
            weekday_map = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
            
            if "周" in date_desc or "星期" in date_desc:
                for key, value in weekday_map.items():
                    if f"周{key}" in date_desc or f"星期{key}" in date_desc:
                        # 计算目标星期几与今天的差距
                        current_weekday = today.weekday()
                        days_ahead = value - current_weekday
                        if days_ahead <= 0:  # 如果目标星期几已经过了，则计算下周
                            days_ahead += 7
                        target_date = today + timedelta(days=days_ahead)
                        logger.info(f"识别为周{key}: {target_date.strftime('%Y-%m-%d')}, 当前周{current_weekday}")
                        return target_date
            
            # 其他情况返回今天
            logger.info(f"无法解析日期描述'{date_desc}'，默认使用今天: {today.strftime('%Y-%m-%d')}")
            return today
        except Exception as e:
            logger.error(f"日期解析失败: {str(e)}")
            logger.info(f"解析失败，默认使用今天: {today.strftime('%Y-%m-%d')}")
            return today
    
    def _process_live_weather(self, data: Dict[str, Any], city: str) -> Dict[str, Any]:
        """处理高德实时天气数据
        
        Args:
            data (Dict[str, Any]): API返回的数据
            city (str): 城市名称
            
        Returns:
            Dict[str, Any]: 处理后的天气信息
        """
        try:
            # 提取实时天气信息
            forecast = data.get("forecasts", [{}])[0]
            casts = forecast.get("casts", [])
            
            if not casts:
                return self._get_error_response("未获取到实时天气数据")
            
            # 获取地理位置信息
            location = forecast.get("city", city)
            
            return {
                "success": True,
                "message": "获取天气信息成功",
                "data": {
                    "city": location,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "weather": casts[0].get("dayweather", "未知"),
                    "temperature": casts[0].get("daytemp", "未知"),
                    "wind_direction": casts[0].get("daywind", "未知"),
                    "wind_power": casts[0].get("daypower", "未知"),
                    "humidity": f"{casts[0].get('nighthumidity', '未知')}%",
                    "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_forecast": False
                },
                "raw_api_response": data
            }
        except Exception as e:
            logger.error(f"处理实时天气数据失败: {str(e)}")
            return self._get_error_response("处理天气数据失败")
    
    def _process_forecast(self, data: Dict[str, Any], city: str, target_date: datetime) -> Dict[str, Any]:
        """处理高德天气预报数据
        
        Args:
            data (Dict[str, Any]): API返回的数据
            city (str): 城市名称
            target_date (datetime): 目标日期
            
        Returns:
            Dict[str, Any]: 处理后的天气信息
        """
        try:
            # 提取预报信息
            forecast = data.get("forecasts", [{}])[0]
            casts = forecast.get("casts", [])
            
            if not casts:
                return self._get_error_response("未获取到天气预报数据")
            
            # 获取地理位置信息
            location = forecast.get("city", city)
            
            # 计算目标日期与今天的天数差
            today = datetime.now().date()
            days_diff = (target_date.date() - today).days
            
            # 检查是否超出预报范围（通常为7天）
            if days_diff >= len(casts):
                return self._get_error_response("超出天气预报范围")
            
            # 获取目标日期的预报
            cast = casts[days_diff]
            
            return {
                "success": True,
                "message": "获取天气预报成功",
                "data": {
                    "city": location,
                    "date": cast.get("date", target_date.strftime("%Y-%m-%d")),
                    "weather": cast.get("dayweather", "未知"),
                    "temperature": f"{cast.get('nighttemp', '未知')}~{cast.get('daytemp', '未知')}",
                    "wind_direction": cast.get("daywind", "未知"),
                    "wind_power": cast.get("daypower", "未知"),
                    "is_forecast": True
                },
                "raw_api_response": data
            }
        except Exception as e:
            logger.error(f"处理天气预报数据失败: {str(e)}")
            return self._get_error_response("处理天气预报数据失败")
    
    def _get_mock_weather(self, city: str, date_str: str, is_forecast: bool) -> Dict[str, Any]:
        """获取模拟天气数据（当API密钥未配置时使用）
        
        Args:
            city (str): 城市名称
            date_str (str): 日期字符串
            is_forecast (bool): 是否为预报
            
        Returns:
            Dict[str, Any]: 模拟的天气信息
        """
        weather_types = ["晴", "多云", "阴", "小雨", "中雨", "大雨", "雷阵雨", "小雪", "中雪", "大雪"]
        wind_directions = ["东", "南", "西", "北", "东北", "东南", "西北", "西南"]
        
        # 使用城市名和日期生成伪随机数，确保同一城市同一天返回相同结果
        import hashlib
        seed = int(hashlib.md5(f"{city}{date_str}".encode()).hexdigest(), 16) % 100000
        import random
        random.seed(seed)
        
        weather = random.choice(weather_types)
        
        # 创建模拟的原始API响应
        mock_raw_response = {
            "status": "1",
            "info": "OK",
            "forecasts": [
                {
                    "city": city,
                    "casts": [
                        {
                            "date": date_str,
                            "dayweather": weather,
                            "nightweather": weather,
                            "daytemp": str(random.randint(15, 30)),
                            "nighttemp": str(random.randint(10, 20)),
                            "daywind": random.choice(wind_directions),
                            "nightwind": random.choice(wind_directions),
                            "daypower": f"{random.randint(1, 6)}级",
                            "nightpower": f"{random.randint(1, 6)}级"
                        }
                    ]
                }
            ]
        }
        
        if is_forecast:
            # 生成7天的模拟预报
            for i in range(1, 7):
                forecast_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                mock_raw_response["forecasts"][0]["casts"].append({
                    "date": forecast_date,
                    "dayweather": random.choice(weather_types),
                    "nightweather": random.choice(weather_types),
                    "daytemp": str(random.randint(15, 30)),
                    "nighttemp": str(random.randint(10, 20)),
                    "daywind": random.choice(wind_directions),
                    "nightwind": random.choice(wind_directions),
                    "daypower": f"{random.randint(1, 6)}级",
                    "nightpower": f"{random.randint(1, 6)}级"
                })
            
            # 获取与目标日期对应的预报
            days_diff = (datetime.strptime(date_str, "%Y-%m-%d").date() - datetime.now().date()).days
            if 0 <= days_diff < len(mock_raw_response["forecasts"][0]["casts"]):
                target_forecast = mock_raw_response["forecasts"][0]["casts"][days_diff]
                
                return {
                    "success": True,
                    "message": "模拟天气预报数据",
                    "data": {
                        "city": city,
                        "date": date_str,
                        "weather": target_forecast["dayweather"],
                        "temperature": f"{target_forecast['nighttemp']}~{target_forecast['daytemp']}",
                        "wind_direction": target_forecast["daywind"],
                        "wind_power": target_forecast["daypower"],
                        "is_forecast": True,
                        "is_mock": True
                    },
                    "raw_api_response": mock_raw_response
                }
            else:
                # 如果日期超出范围，返回默认数据
                return {
                    "success": True,
                    "message": "模拟天气预报数据",
                    "data": {
                        "city": city,
                        "date": date_str,
                        "weather": weather,
                        "temperature": f"{random.randint(10, 20)}~{random.randint(15, 30)}",
                        "wind_direction": random.choice(wind_directions),
                        "wind_power": f"{random.randint(1, 6)}级",
                        "is_forecast": True,
                        "is_mock": True
                    },
                    "raw_api_response": mock_raw_response
                }
        else:
            # 模拟实时天气数据
            return {
                "success": True,
                "message": "模拟实时天气数据",
                "data": {
                    "city": city,
                    "date": date_str,
                    "weather": weather,
                    "temperature": str(random.randint(15, 30)),
                    "wind_direction": random.choice(wind_directions),
                    "wind_power": f"{random.randint(1, 6)}级",
                    "humidity": f"{random.randint(30, 90)}%",
                    "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_forecast": False,
                    "is_mock": True
                },
                "raw_api_response": mock_raw_response
            }
    
    def _get_error_response(self, error_msg: str) -> Dict[str, Any]:
        """生成错误响应
        
        Args:
            error_msg (str): 错误信息
            
        Returns:
            Dict[str, Any]: 错误响应
        """
        return {
            "success": False,
            "message": error_msg,
            "data": {
                "weather": "未知",
                "temperature": "未知"
            },
            "raw_api_response": None
        }
