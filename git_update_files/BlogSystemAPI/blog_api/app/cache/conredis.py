#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : conredis.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:54
@Desc    : 
"""
import redis
from redis.asyncio import Redis, ConnectionPool

from app.configuration.config import settings


class RedisClient(object):
    __instance = None

    @classmethod
    async def get_client(cls) -> Redis:
        if cls.__instance is None:
            # 创建连接池，提高并发性
            pool = ConnectionPool.from_url(settings.REDIS_URL, max_connections=100, decode_responses=True)
            cls.__instance = Redis(connection_pool=pool)    # 创建redis实例
        return cls.__instance

    @classmethod
    async def init(cls):
        return await cls.get_client()

    @classmethod
    async def close(cls):
        if cls.__instance:
            await cls.__instance.close()
            cls.__instance = None
            print("Redis连接已关闭")


async def get_unique_id(redis_client: redis.Redis, key: str="global url id") -> int:
    return await redis_client.incr(key)


async def get_redis_client() -> Redis:
    return await RedisClient.get_client()
