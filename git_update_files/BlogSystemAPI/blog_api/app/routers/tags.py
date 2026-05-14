#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : tags.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/11 14:31
@Desc    : 
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User

from app.authen import get_current_user
from app.configuration.database import get_db
from app.models import Articles, Tags

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)


@router.get("/{tag_name}")
async def get_tags(
        tags_name: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 10
):
    if not current_user:
        raise HTTPException(status_code=401, detail="找不到当前用户，请先去登录")
    stmt = select(Articles).join(Articles.tags).where(Tags.name == tags_name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
