from fastapi import status, HTTPException, UploadFile
from src.config import settings
from src.models import Video, User
from typing import List


def check_file_type(file: UploadFile, allowed_types: List[str]) -> None:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Unsupported type of file was given"
        )

        
def check_files_types(video_file: UploadFile, cover_file: UploadFile) -> None:
    check_file_type(video_file, settings.ALLOWED_VIDEO_MEDIA_TYPES)
    check_file_type(cover_file, settings.ALLOWED_COVER_MEDIA_TYPES)
    

def check_video_exists(video: Video):
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found") 


def check_channel_access(video: Video, user: User):
    if video.channel not in user.channels:
        raise HTTPException(status_code=403, detail="Access denied")
    
    
def check_video(video: Video, user: User):
    check_video_exists(video)
    check_channel_access(video, user)
    