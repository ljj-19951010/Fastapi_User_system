#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : app
@File    : database.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/12 10:18
@Desc    : 
"""
import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config import settings

logger = logging.getLogger(__name__)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,     # 打印SQL语句
    future=True,            # 使用异步引擎
    echo_pool=False,        # 打印连接池信息
    pool_pre_ping=True,         # 检查数据库连接是否有效，（必须有）
    pool_size=settings.DB_POOL_SIZE,        # 连接池大小
    max_overflow=settings.DB_MAX_OVERFLOW,          # 连接池溢出大小
    pool_timeout=settings.DB_POOL_TIMEOUT,        # 连接池超时时间
    pool_recycle=settings.DB_POOL_RECYCLE,        # 连接池回收时间
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    依赖注入
    获取数据库会话，异常自动回滚，自动关闭会话
    :return:
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# 检查数据库连接是否正常
async def check_db_health() -> bool:
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def close_db_connections():
    """
    关闭数据库连接
    :return:
    """
    await engine.dispose()
    logger.info("Database connections closed")


def get_pool_status():
    pool = engine.pool
    return {
        "size": pool.size(),
        "overflow": pool.overflow(),
        "in_use": pool.checkedout(),
        "available": pool.available(),
        "checked_in": pool.checkedin(),
        "total": pool.total()
    }