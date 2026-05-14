#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : schemas.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:57
@Desc    : 
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBriefOut(BaseModel):
    username: str
    model_config = ConfigDict(from_attributes=True)


class CategoryBriefOut(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class TagBriefOut(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class ArticleOut(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    views: int = 0
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    tags: list[TagBriefOut] = []
    author: UserBriefOut
    category: Optional[CategoryBriefOut] = None      # 分类名
    model_config = ConfigDict(from_attributes=True)


class CreateArticle(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    tags: Optional[list[str]] = []
    category_id: Optional[int] = 0
    user_id: int


class UpdateArticle(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    tags: Optional[list[str]] = []


class UserOut(BaseModel):
    """
    API界面 显示的用户信息
    """
    username: str
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    articles_count: int = 0
    is_superuser: bool
    model_config = ConfigDict(from_attributes=True)


class CreateUser(BaseModel):
    """
    创建用户时，需要传递的参数，添加到数据库
    """
    username: str
    password: str
    email: str
    bio: str
    avatar: str
    is_superuser: bool = False


class UpdateUser(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None


class CategoryOut(BaseModel):
    name: str
    slug: Optional[str] = None
    articles: list[ArticleOut] = []
    model_config = ConfigDict(from_attributes=True)


class TagsOut(BaseModel):
    name: str
    slug: Optional[str] = None
    articles: list[ArticleOut] = []
    model_config = ConfigDict(from_attributes=True)
