#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : authen.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:57
@Desc    : 
"""
from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash

from app.configuration.config import settings
from app.configuration.database import get_db
from app.models import Users
from app.schemas import TokenData

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2PasswordBearer会自动解析请求头中的Authorization字段，并提取出token
OAuth2_schema = OAuth2PasswordBearer(tokenUrl="/users/login")


# 生成token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:           # 如果传入了过期时间
        expire = datetime.utcnow() + expires_delta
    else:
        # 如果没有传入过期时间
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})       # 更新token数据字典
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)        # 生成token
    return encoded_jwt


# 验证token
async def validate_token(token: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token认证错误",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        raise credentials_exception


# 将明文密码转hash密码
def hash_password(password: str) -> str:
    return generate_password_hash(password=password)


# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, plain_password)


# 获取当前用户
async def get_current_user(token: str = Depends(OAuth2_schema), db: AsyncSession = Depends(get_db)) -> Users:
    # 获取token中的用户名
    token_data = await validate_token(token)
    # 根据用户名查询用户
    result = await db.execute(select(Users).where(Users.username == token_data.username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# 获取当前用户权限
async def get_current_user_scopes(current_user: Users = Depends(get_current_user)) -> bool:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="你不是管理员,没有权限")
    return True
