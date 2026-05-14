#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : app
@File    : authens.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/12 11:05
@Desc    : 
"""
from datetime import timedelta, datetime

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash

from config import settings
from database import get_db
from models import User
from schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


async def create_token(data: dict, expires_delta: timedelta | None = None):
    """
    创建token
    :param data: 传进来用户信息的字典
    :param expires_delta: 设置token过期时间
    :return:
    """
    to_encode = data.copy()
    try:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception:
        raise HTTPException(status_code=500, detail="create token error")


async def validate_token(token: str):
    """
    验证token
    :param token: 传进来的token数据
    :return: 将数据返回给前端验证
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="用户名发生错误，Token无法继续验证")
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效，无法通过验证")


async def hash_password(password: str) -> str:
    """
    将明文密码转hash密码
    :param password: 传进来的明文密码
    :return: 返回hash密码
    """
    return generate_password_hash(password=password)


async def check_password(hashed_password: str, password: str) -> bool:
    """
    验证密码
    :param password: 传进来的明文密码
    :param hashed_password: 传进来的hash密码
    :return: 返回验证结果
    """
    return check_password_hash(hashed_password, password)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    获取当前用户
    :param token: 传进来的token
    :param db: 数据库连接
    :return: 返回当前用户
    """
    # 获取token中的用户名
    token_data = await validate_token(token)
    # 根据用户名查询用户
    result = await db.execute(select(User).where(User.username == token_data.username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


async def get_supper_user(current_user: User = Depends(get_current_user)) -> bool:
    """
    获取当前用户权限
    :param current_user: 传进来的当前用户
    :return: 返回当前用户权限
    """
    if not current_user.is_supper:
        raise HTTPException(status_code=403, detail="你不是管理员,没有权限")
    return True

