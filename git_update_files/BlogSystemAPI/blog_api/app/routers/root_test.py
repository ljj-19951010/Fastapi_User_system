#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : root_test.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:58
@Desc    : 
"""
from fastapi import APIRouter

router = APIRouter(
    prefix="/test",
    tags=["test"]
)


@router.get("/test")
async def test():
    return {"detail": "I am a tea pot!"}
