#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : users.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/7 9:52
@Desc    : 
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.authen import hash_password, verify_password, create_access_token, get_current_user_scopes, get_current_user
from app.configuration.database import get_db
from app.models import Users
from app.schemas import CreateUser, UserOut, Token, UpdateUser
from app.untils.myException import HTTPExceptionResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post('/register', response_model=UserOut)
async def register(new_user: CreateUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).where(Users.username == new_user.username))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user_dict = new_user.model_dump(exclude={"password"})           # 排除password字段
    user_dict["hash_password"] = hash_password(new_user.password)       # 重新添加模型中对应的字段
    new_user = Users(**user_dict)           # 必须对应模型的字段
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    print("注册成功")
    return new_user


@router.post('/login', response_model=Token)
async def login(new_user: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).where(Users.username == new_user.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="用户名不存在")
    if not verify_password(new_user.password, user.hash_password):       # 验证密码
        raise HTTPException(status_code=400, detail="密码错误")
    access_token = create_access_token(data={'sub': user.username})
    print("登录成功")
    return {"access_token": access_token, "token_type": "bearer"}


# 显示所有用户，管理员权限
@router.get('/', response_model=list[UserOut])
async def get_users(current_user: Users = Depends(get_current_user),
                    superuser: Users = Depends(get_current_user_scopes),
                    db: AsyncSession = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=404, detail="你还没登陆，先去登录")
    if not superuser:
        raise HTTPException(status_code=403, detail="你不是管理员,没有权限")
    result = await db.execute(select(Users))
    return result.scalars().all()


# 删除用户，管理员权限
@router.delete('/{username}', response_model=UserOut)
async def delete_user(
        username: str,
        current_user: Users = Depends(get_current_user),
        superuser: Users = Depends(get_current_user_scopes),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=404, detail="你还没登陆，先去登录")
    if not superuser:
        raise HTTPException(status_code=403, detail="你不是管理员,没有权限")
    result = await db.execute(select(Users).where(Users.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.commit()
    HTTPExceptionResponse(code=200, message="删除成功")


# 更新用户信息，需要权限（当前用户只能更改自己的信息，管理员用户可以更改所有人的信息）
@router.put('/{username}', response_model=UserOut)
async def update_user(
        username: str,
        user_in: UpdateUser,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user.is_superuser and current_user.username != username:
        raise HTTPException(status_code=403, detail="无权限修改该用户的信息")
    result = await db.execute(select(Users).where(Users.username == username))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_data = user_in.model_dump(exclude_unset=True)        # 排除未设置的字段
    if 'password' in update_data:
        target_user.hash_password = hash_password(update_data['password'])
    for value, field in update_data.items():
        if hasattr(target_user, value):         # 检查该对象是否有该属性，返回bool值
            setattr(target_user, value, field)          # 动态赋值
    await db.commit()
    await db.refresh(target_user)
    return target_user
