from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, APIRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from src.limiter import limiter
from src.config import settings
from src.auth.service import auth_router
from src.channels.service import channels_router
from src.videos.service import videos_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        redis = Redis(
            host=settings.cache.host,
            port=settings.cache.port,
            db=settings.cache.db
        )
        
        FastAPICache.init(RedisBackend(redis), prefix=settings.cache.prefix)
        
        yield
    finally:
        await redis.close()

# app configuration
app = FastAPI(
    title=settings.api_name,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# routers including 
main_router = APIRouter(prefix=settings.prefix)

main_router.include_router(auth_router, tags=["Auth"])
main_router.include_router(channels_router, tags=["Channels"])
main_router.include_router(videos_router, tags=["Videos"])

app.include_router(main_router)
