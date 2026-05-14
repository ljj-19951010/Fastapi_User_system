#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : comments.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:53
@Desc    : 
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.authen import get_current_user
from app.configuration.database import get_db
from app.models import Users, Articles, Comments

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)



@router.get("/{article_id}")
async def get_comments(
        artcile_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=404, detail="你还没登陆")
    stmt = select(Comments).where(Comments.article_id == artcile_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    return comment