#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : articles.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:52
@Desc    : 
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.authen import get_current_user, get_current_user_scopes
from app.configuration.database import get_db
from app.models import Articles, Users, Tags, article_tag
from app.schemas import ArticleOut, CreateArticle, UpdateArticle
from app.untils.tags_to_list import parse_tags

router = APIRouter(
    prefix="/articles",
    tags=["articles"]
)


async def add_tags(tags: list, article: Articles, db: AsyncSession):
    # 先删掉关联的旧标签
    await db.execute(article_tag.delete().where(article_tag.c.article_id == article.id))

    for tag in tags:
        # 查询标签是否存在
        result = await db.execute(select(Tags).where(Tags.name == tag))
        tag_obj = result.scalar_one_or_none()
        # 如果标签不存在，则创建标签，将要创建的标签直接替换查询的结果
        if not tag_obj:
            tag_obj = Tags(name=tag)            # 创建标签对象
            db.add(tag_obj)         # 添加到数据库
            await db.flush()        # 刷新表，不然不会生成新的id
        # 如果标签存在，或者已经添加完标签，给文章表和标签表 添加关联
        await db.execute(article_tag.insert().values(article_id=article.id, tag_id=tag_obj.id))


# 获取所有文章 任何人都可以看
@router.get("/", response_model=List[ArticleOut])
async def read_articles(db: AsyncSession = Depends(get_db)):
    stmt = select(Articles).options(
        selectinload(Articles.tags),
        selectinload(Articles.author),
        selectinload(Articles.comments),
        selectinload(Articles.category)
    ).order_by(Articles.id.desc())
    result = await db.execute(stmt)
    articles = result.unique().scalars().all()
    return articles


# 获取当前用户的所有文章
@router.get("/my_article", response_model=List[ArticleOut])
async def read_user_articles(
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if not current_user:
        return HTTPException(status_code=401, detail="用户未登录")
    stmt = select(Articles).where(Articles.user_id == current_user.id).options(
        selectinload(Articles.tags),
        selectinload(Articles.author),
        selectinload(Articles.comments),
        selectinload(Articles.category)
    )
    result = await db.execute(stmt)
    articles = result.unique().scalars().all()
    return articles


# 当前用户创建自己的文章
@router.post("/add_article")
async def create_article(
        article: CreateArticle,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return HTTPException(status_code=401, detail="用户未登录")
    article_dict = article.model_dump(exclude={"user_id"})
    article_dict["user_id"] = current_user.id
    if not article.category_id:
        article_dict["category_id"] = None
    new_article = Articles(**article_dict)
    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    print(f"新文章已创建!{new_article}")
    return {"code": 200, "message": "文章创建成功"}


# 当前用户修改自己的文章
@router.put("/update_article/{article_id}")
async def update_article(
        article_id: int,
        article_in: UpdateArticle,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")

    stmt = select(Articles).where(Articles.id == article_id, Articles.user_id == current_user.id).options(
        selectinload(Articles.tags),
        selectinload(Articles.author),
        selectinload(Articles.comments),
        selectinload(Articles.category)
    )
    result = await db.execute(stmt)
    article = result.unique().scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    article_data = article_in.model_dump(exclude_unset=True)        # 只更新有值的字段
    tags = article_data.pop("tags", None)
    for key, value in article_data.items():
        if hasattr(article, key):
            setattr(article, key, value)
    if tags:
        tag = parse_tags(tags)
        await add_tags(tags=tag, article=article, db=db)

    await db.commit()
    await db.refresh(article)
    return {"code": 200, "message": "文章更新成功"}


# 当前用户删除自己的文章
@router.delete("/delete_article/{article_id}")
async def delete_article(
        article_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")
    stmt = select(Articles).where(Articles.id == article_id, Articles.user_id == current_user.id).options(
        selectinload(Articles.tags),
        selectinload(Articles.author),
        selectinload(Articles.comments),
        selectinload(Articles.category)
    )
    result = await db.execute(stmt)
    article = result.unique().scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或无权限删除")
    await db.delete(article)
    await db.commit()
    return {"code": 200, "message": "文章删除成功"}


# 管理员用户 管理所有的文章
@router.post('/update_article_admin/{article_id}')
async def update_article_admin(
        article_id: int,
        article_in: UpdateArticle,
        current_user: Users = Depends(get_current_user),
        supper_user: Users = Depends(get_current_user_scopes),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")
    if not supper_user:
        raise HTTPException(status_code=403, detail="你没有权限更改该文章!")

    stmt = select(Articles).where(Articles.id == article_id).options(
        selectinload(Articles.tags),
        selectinload(Articles.author),
        selectinload(Articles.comments),
        selectinload(Articles.category)
    )
    result = await db.execute(stmt)
    article = result.unique().scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    article_data = article_in.model_dump(exclude_unset=True)  # 只更新有值的字段
    tags = article_data.pop("tags", None)

    for key, value in article_data.items():
        if hasattr(article, key):
            setattr(article, key, value)
    if tags:
        tag = parse_tags(tags)
        await add_tags(tags=tag, article=article, db=db)

    await db.commit()
    await db.refresh(article)
    return {"code": 200, "message": "文章更新成功"}


# 管理员用户可以删除所有的文章
@router.delete('/delete_article_admin/{article_id}')
async def delete_article_admin(
        article_id: int,
        current_user: Users = Depends(get_current_user),
        supper_user: Users = Depends(get_current_user_scopes),
        db: AsyncSession = Depends(get_db),

):
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未登录")
    if not supper_user:
        raise HTTPException(status_code=403, detail="你没有权限删除该文章!")

    article = await db.get(Articles, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    await db.delete(article)
    await db.commit()
    return {"code": 200, "message": "文章删除成功"}
