#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : myException.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/8 9:58
@Desc    : 自定义响应模块
"""
from fastapi import HTTPException


def HTTPExceptionResponse(code, message, headers={"WWW-Authenticate": "Bearer"}):
    """自定义异常"""
    raise HTTPException(status_code=code, detail=message, headers=headers)