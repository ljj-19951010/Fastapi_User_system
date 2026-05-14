#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : models.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:56
@Desc    :
关键字参数描述：
cascade 参数定义了当对父对象执行某些操作（如保存、删除）时，是否要“级联”到与之关联的子对象。
"all"：是 save-update, merge, refresh-expire, expunge, delete 的简写，表示几乎所有操作都会级联。
"delete-orphan"：当一个子对象不再被任何父对象引用时，自动将其删除。
组合 "all, delete-orphan" 意味着：
    当你添加或删除关联对象时，操作会自动同步到数据库。
    当你删除父对象时，所有关联的子对象也会被删除。
    当你把子对象从父对象的集合中移除（且没有其他父对象引用它）时，该子对象会自动从数据库中删除

index=True 为数据库创建索引，提高查询效率，一般用于高频查询的字段，不是所有的字段都加索引好
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import relationship

from app.configuration.database import Base


# 多对多关系表，一般不单独定义模型类
article_tag = Table(
    'article_tag',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True, index=True),        # 外键,关联文章表
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True, index=True)          # 外键,关联标签表
)


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, index=True, unique=True)       # 用户名
    hash_password = Column(Text, nullable=False)           # 密码
    email = Column(String(255), nullable=True, index=True, unique=True)           # 邮箱
    bio = Column(Text, nullable=True)           # 个人简介
    avatar = Column(String(255), nullable=True)         # 头像地址
    is_superuser = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    articles = relationship('Articles', back_populates='author', cascade="all, delete-orphan")      # 一对多关系,一个用户可以有多篇文章
    comments = relationship('Comments', back_populates='author', cascade="all, delete-orphan")      # 一对多关系,一个用户可以有多条评论


class Articles(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)       # 外键,关联用户表
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=True, index=True)       # 外键,关联分类表,可以为空

    title = Column(String(255), nullable=False, index=True)      # 文章标题
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=False, default='')         # 摘要
    views = Column(Integer, nullable=False, default=0)           # 浏览量

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author = relationship('Users', back_populates='articles')       # 一对多关系,一个用户可以有多篇文章
    comments = relationship('Comments', back_populates='articles', cascade="all, delete-orphan")  # 一对多关系,一篇文章可以有多条评论
    category = relationship('Categories', back_populates='articles')        # 一对多关系,一个分类可以有多篇文章
    tags = relationship('Tags', secondary=article_tag, back_populates='articles')  # 多对多关系,一篇文章可以有多标签,一个标签可以有多篇文章


class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)      # 标签名称
    slug = Column(String(255), nullable=True, default='')      # 标签别名

    articles = relationship('Articles', secondary=article_tag, back_populates='tags')       # 多对多关系,一篇文章可以有多标签,一个标签可以有多篇文章


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)      # 分类名称
    slug = Column(String(255), nullable=True, default='', index=True)      # 分类别名
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    articles = relationship('Articles', back_populates='category')  # 一对多关系,一个分类可以有多篇文章


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)       # 外键,关联用户表
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)       # 外键,关联文章表
    parent_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)       # 外键,关联评论表,可以为空

    content = Column(Text, nullable=False)           # 评论内容
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    author = relationship('Users', back_populates='comments')       # 一对多关系,一个用户可以有多条评论
    articles = relationship('Articles', back_populates='comments')       # 一对多, 一篇文章可以有多条评论
    # 同一个表中的关系
    parent = relationship('Comments', remote_side=[id], back_populates='replies')       # 一对多, 一条评论可以有多条子评论
    replies = relationship('Comments', back_populates='parent', cascade='all, delete-orphan')       # 一对多, 一条评论可以有多条子评论