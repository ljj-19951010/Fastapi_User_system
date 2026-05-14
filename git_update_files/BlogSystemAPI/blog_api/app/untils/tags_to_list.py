#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : blog_api
@File    : tags_to_list.py
@IDE     : PyCharm
@Author  : Jinjing
@Date    : 2026/5/9 11:18
@Desc    : 将前端传来的tags数据转换成列表
"""
import json


def parse_tags(tags):
    # 如果tags是字符串，则尝试将其转换为列表
    if isinstance(tags, str):
        try:
            # 如果tags是json字符串，则尝试将其转换为列表
            tags_list = json.loads(tags)            # json.loads()将字符串转换为列表， tags可能是"["xx"]"这种
            if isinstance(tags_list, list):     # 如果tags_list是列表，则直接返回
                return tags_list
        except:
            pass
        return [tags]
    # 如果tags是列表，则直接返回
    elif isinstance(tags, list):
        return tags
    # 如果tags既不是字符串也不是列表，则返回空列表
    else:
        return []