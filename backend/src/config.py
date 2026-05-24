import os 
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent


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
        env_file=BASE_DIR.parent / ".env" if os.getenv("LOAD_DOTENV", "1") != "0" else None,
        env_file_encoding="utf-8",  
    )
    # media variables 
    ALLOWED_COVER_MEDIA_TYPES: List[str] = [
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]
    
    ALLOWED_VIDEO_MEDIA_TYPES: List[str] = ["video/mp4"]
settings: Settings = Settings()

