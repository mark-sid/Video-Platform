from fastapi import FastAPI, APIRouter

from src.config import settings
from src.auth.service import auth_router
from src.channels.service import channels_router
from src.videos.service import videos_router

app = FastAPI(
    title=settings.api_name,
    description=settings.api_description,
    version=settings.api_version
)

main_router = APIRouter(prefix=settings.prefix)

main_router.include_router(auth_router, tags=["Getting started"])
main_router.include_router(channels_router, tags=["Channels"])
main_router.include_router(videos_router, tags=["Videos"])

app.include_router(main_router)
