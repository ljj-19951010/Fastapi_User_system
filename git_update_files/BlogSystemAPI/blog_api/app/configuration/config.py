#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : config.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:56
@Desc    : 
"""
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".envs"
        env_file_encoding = "utf-8"


settings = Settings()
