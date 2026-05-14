#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : categories.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:53
@Desc    : 分类查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.authen import get_current_user
from app.configuration.database import get_db
from app.models import Articles, Users
from app.schemas import ArticleOut

router = APIRouter(
    prefix="/category",
    tags=["category"]
)


@router.get("/", response_model=list[ArticleOut])
async def read_category_articles(
        category_id: int = Query(..., description="分类id"),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    stmt = select(Articles).where(Articles.user_id == current_user.id, Articles.category_id == category_id).options(
        selectinload(Articles.category),
        selectinload(Articles.author),
        selectinload(Articles.tags),
        selectinload(Articles.comments)

    )
    result = await db.execute(stmt)
    return result.scalars().all()
