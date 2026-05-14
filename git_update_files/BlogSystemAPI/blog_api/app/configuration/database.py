#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : database.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:56
@Desc    : 
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.configuration.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=True,      # 是否打印SQL语句
    future=True     # 使用异步引擎
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False      # 事务提交后，会话不会自动关闭
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("数据库初始化完成(数据表架构创建完成)")


async def close_db():
    await engine.dispose()
    print("数据库连接关闭")
