#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PostgreSQL仓储实现模块
"""

import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import JSONB

from app.config import settings
from app.domain.entity.intent import Intent, IntentType
from app.domain.repository.intent_repository import IntentRepository
from app.common.logging.logger import log_manager

# 创建日志器
logger = log_manager.get_logger("postgres_repository")

# 创建SQLAlchemy基类
Base = declarative_base()


class IntentRecord(Base):
    """意图记录表模型"""
    
    __tablename__ = "intent_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    intent_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    entities = Column(JSONB, nullable=False)  # 使用PostgreSQL的JSONB类型
    created_at = Column(DateTime, default=datetime.now)


class PostgresIntentRepository(IntentRepository):
    """PostgreSQL意图仓储实现"""
    
    def __init__(self):
        """初始化PostgreSQL仓储"""
        # 创建数据库引擎
        self.engine = create_engine(settings.DATABASE_URL)
        
        # 创建表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        logger.info("PostgreSQL意图仓储初始化完成")
    
    async def save(self, intent: Intent) -> None:
        """保存意图记录

        Args:
            intent (Intent): 意图实体
        """
        with self.Session() as session:
            # 创建记录
            record = IntentRecord(
                intent_type=intent.type.value,
                confidence=intent.confidence,
                text=intent.text,
                entities=intent.entities  # 直接存储JSON，无需转换
            )
            
            # 添加并提交
            session.add(record)
            session.commit()
            logger.debug(f"保存意图记录成功: {intent.text}")
    
    async def find_by_text(self, text: str) -> Optional[Intent]:
        """根据文本查找意图

        Args:
            text (str): 文本内容

        Returns:
            Optional[Intent]: 意图实体，如果不存在则返回None
        """
        with self.Session() as session:
            # 查询记录
            stmt = select(IntentRecord).where(IntentRecord.text == text)
            result = session.execute(stmt).scalars().first()
            
            # 如果找到记录，转换为实体
            if result:
                logger.debug(f"找到匹配文本的意图记录: {text}")
                return Intent(
                    type=IntentType(result.intent_type),
                    confidence=result.confidence,
                    text=result.text,
                    entities=result.entities  # 直接获取，无需转换
                )
            
            logger.debug(f"未找到匹配文本的意图记录: {text}")
            return None
    
    async def find_recent(self, limit: int = 10) -> List[Intent]:
        """查询最近的意图记录

        Args:
            limit (int, optional): 返回记录数量限制. 默认为10.

        Returns:
            List[Intent]: 意图记录列表
        """
        with self.Session() as session:
            # 查询最近记录
            stmt = select(IntentRecord).order_by(IntentRecord.created_at.desc()).limit(limit)
            results = session.execute(stmt).scalars().all()
            
            # 转换为实体列表
            intents = [
                Intent(
                    type=IntentType(record.intent_type),
                    confidence=record.confidence,
                    text=record.text,
                    entities=record.entities  # 直接获取，无需转换
                )
                for record in results
            ]
            
            logger.debug(f"查询到{len(intents)}条最近意图记录")
            return intents
