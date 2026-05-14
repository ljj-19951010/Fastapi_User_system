from fastapi import FastAPI

from app.configuration.database import init_db
from app.routers import users, root_test, articles, categories, comments, tags

app = FastAPI()

app.include_router(root_test.router)            # 测试
app.include_router(users.router)        # 用户模块
app.include_router(articles.router)     # 文章模块
app.include_router(categories.router)       # 分类模块
app.include_router(comments.router)       # 评论模块
app.include_router(tags.router)            # 标签模块


@app.on_event("startup")
async def startup():
    await init_db()