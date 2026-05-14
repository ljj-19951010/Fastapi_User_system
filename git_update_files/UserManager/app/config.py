#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : app
@File    : config.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/12 10:18
@Desc    : 
"""
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str     # 加密算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10           # token过期时间
    DB_POOL_SIZE: int = 10      # 数据库连接池大小
    DB_MAX_OVERFLOW: int = 20        # 数据库连接池最大溢出连接数
    DB_POOL_TIMEOUT: int = 30      # 数据库连接池超时时间
    DB_POOL_RECYCLE: int = 1800      # 数据库连接池连接回收时间

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()