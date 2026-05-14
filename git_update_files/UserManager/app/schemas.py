#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : app
@File    : schemas.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/12 10:19
@Desc    : 
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserInfoOut(BaseModel):
    name: str
    gender: str
    birthday: str
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UpdateUserInfo(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(BaseModel):
    username: str
    email: str
    is_supper: bool
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class CreateUser(BaseModel):
    username: str
    password: str
    email: str
    is_supper: bool = False
    is_active: bool = True


class UpdateUser(BaseModel):
    password: Optional[str] = None
    email: Optional[str] = None


class UpdateUserSupper(BaseModel):
    password: Optional[str] = None
    email: Optional[str] = None
    is_supper: Optional[bool] = None
    is_active: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
