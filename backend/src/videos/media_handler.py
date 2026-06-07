import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile, HTTPException, status

from src.config import settings


def get_unique_filename(filename: str) -> str:
    """Function to generate unique filename"""
    name, ext = Path(filename).stem, Path(filename).suffix
    return f"{uuid.uuid4()}_{name}{ext}"


def get_media_path(user_id: int, media_type: str, filename: str) -> Path:
    """Function to get media saving path"""
    return Path(settings.media_path) / str(user_id) / media_type / filename


async def save_file(file: UploadFile, user_id: int) -> Tuple[str, str]:
    """Function to save file safetly"""
    try:
        if file.content_type in settings.ALLOWED_COVER_MEDIA_TYPES:
            media_type = "covers"
        else:
            media_type = "videos"

        new_filename = get_unique_filename(file.filename)
        file_path = get_media_path(user_id, media_type, new_filename)
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)
                
        return str(file_path), new_filename
    except (IOError, OSError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save video"
        ) 


def delete_file(file_path: str) -> None:
    os.remove(file_path)

        



        
    