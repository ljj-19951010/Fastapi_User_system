from contextlib import asynccontextmanager

from fastapi import FastAPI

import user
from database import check_db_health, logger, close_db_connections


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动应用之前检查数据库健康
    if not await check_db_health():
        logger.error("Database unavailable on startup")
    yield
    # 关闭数据库连接，释放连接池
    await close_db_connections()

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

