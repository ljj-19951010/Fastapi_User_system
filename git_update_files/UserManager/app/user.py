#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : app
@File    : user.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/12 10:19
@Desc    : 
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authens import hash_password, get_current_user, check_password, create_token
from database import get_db
from models import User, UserInfo
from schemas import CreateUser, UserResponse, Token, UserInfoOut, UpdateUser, UpdateUserInfo, UpdateUserSupper

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


# 公共逻辑 更新用户
async def _update_user_info(
        user_id: int,
        user_in: UpdateUserInfo,
        db: AsyncSession
):
    stmt = select(UserInfo).where(UserInfo.user_id == user_id)
    result = await db.execute(stmt)
    user_info = result.scalar_one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(user_info, key):
            setattr(user_info, key, value)
    await db.commit()
    await db.refresh(user_info)
    return user_info


@router.post("/register", response_model=UserResponse)
async def register(user: CreateUser, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="账号已存在")
    user_dict = user.model_dump(exclude={"password"})
    user_dict["password"] = await hash_password(user.password)
    new_user = User(**user_dict)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(
        user: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.username == user.username)
    result = await db.execute(stmt)
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=400, detail="用户名不存在")

    hash_pwd = check_password(db_user.password, user.password)
    if not hash_pwd:
        raise HTTPException(status_code=400, detail="密码错误")

    access_token = await create_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.put('/admin/me', response_model=UserResponse)
async def update_user(
        user_in: UpdateUser,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")

    stmt = select(User).where(User.id == current_user.id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = await hash_password(update_data.get("password"))

    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.put('/admin/{userid}', response_model=UserResponse)
async def update_supper_user(
        user_in: UpdateUserSupper,
        userid: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")
    if not current_user.is_supper:
        raise HTTPException(status_code=403, detail="你不是管理员用户!")

    stmt = select(User).where(User.id == userid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = await hash_password(update_data.get("password"))

    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


# 删除用户账户
@router.delete('/admin/{user_id}')
async def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    删除用户账户
    :return:
    """
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")
    if not current_user.is_supper:
        raise HTTPException(status_code=403, detail="你不是管理员用户!")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_supper:
        raise HTTPException(status_code=403, detail="不能删除管理员用户")
    await db.delete(user)
    await db.commit()
    return {"code": 200, "message": f"账户{user.username}删除成功"}


# 以下是对用户信息表操作
@router.get('/', response_model=List[UserInfoOut])
async def get_users_info(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")
    if not current_user.is_supper:
        stmt = select(UserInfo).where(current_user.id == UserInfo.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return [user] if user else []
    users = await db.execute(select(UserInfo))
    return users.scalars().all()


@router.get('/{user_id}', response_model=UserInfoOut)
async def get_user_info(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")
    if not current_user.is_supper:
        raise HTTPException(status_code=403, detail="无权限访问")
    user = await db.get(UserInfo, user_id)
    return user


# 当前用户，只能修改当前用户信息
@router.put('/me', response_model=UserInfoOut)
async def update_me_info(
        user_in: UpdateUserInfo,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")
    return await _update_user_info(current_user.id, user_in, db)


# 管理员用户可以更改所有用户信息
@router.put('/{user_id}', response_model=UserInfoOut)
async def update_user_info(
        user_in: UpdateUserInfo,
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")

    if not current_user.is_supper:
        raise HTTPException(status_code=403, detail="无权限访问")

    return await _update_user_info(user_id, user_in, db)


# 删除用户信息
@router.delete('/{info_id}')
async def delete_user_info(
        info_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    删除用户信息
    :return:
    """
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="用户未登录或已注销")
    if not current_user.is_supper:
        raise HTTPException(status_code=403, detail="无权限访问")

    stmt = select(UserInfo).where(UserInfo.id == info_id)
    result = await db.execute(stmt)
    user_info = result.scalar_one_or_none()
    if not user_info:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user_info.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="不能删除自己的信息")
    await db.delete(user_info)
    await db.commit()
    return {"code": 200, "message": f"{user_info.name}的个人信息删除成功"}