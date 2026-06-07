import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent


class CacheConfig(BaseModel):
    host: str = "localhost"#"redis"
    port: str = "6379"
    db: int = 0
    prefix: str = "cache"


class Settings(BaseSettings):
    # Website description
    api_name: str = "Video platform"
    api_version: str = "v1"
    api_description: str = "API to watch some videos"
    prefix: str = f"/api/{api_version}"
    # databases urls
    database_url: str
    test_database_url: str
    # auth variables
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # media variables
    media_path: Path = BASE_DIR / "media"
    # loading .env
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file= BASE_DIR / "dev.env" if os.environ.get("LOAD_DEV_ENV_FILE", 1)  == 1 else None  
    )
    # media variables 
    ALLOWED_COVER_MEDIA_TYPES: List[str] = [
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]
    
    ALLOWED_VIDEO_MEDIA_TYPES: List[str] = ["video/mp4"]
    # redis 
    cache: CacheConfig = CacheConfig()
    # limiter
    limiter_storage_uri: str = "redis://localhost:6379/1" #"redis://redis:6379/1"
    limiter_default_limits: str ="50/minute"
    
    
settings: Settings = Settings()
