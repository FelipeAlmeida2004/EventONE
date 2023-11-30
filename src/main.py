from fastapi import FastAPI

from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
import time

from src.users.router import router as user_router
from src.reservations.router import router as reservation_router
from src.events.router import router as events_router
from src.comments.router import router as comments_router

from src.config import settings


app = FastAPI(
    title=settings.app_name,
)

app.include_router(user_router)
app.include_router(reservation_router)
app.include_router(events_router)
app.include_router(comments_router)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/long_operation")
@cache(expire=60)
async def long_op():
    time.sleep(3)
    return {"operation": "longo"}