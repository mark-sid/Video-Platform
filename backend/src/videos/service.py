import os
from pathlib import Path
from typing import List, Optional, Annotated

from fastapi import APIRouter, status, HTTPException, UploadFile, Form, File, Query, Request
from fastapi.responses import FileResponse
from fastapi_cache.decorator import cache

from .media_handler import save_file, delete_file
from .schemas import VideoSchema, VideoLazySchema, VideoUpdateSchema, VideoCreateInternal
from .crud import (
    create_video_with_media, 
    get_video, 
    get_media, 
    get_videos, 
    update_video, 
    delete_video_with_media, 
    update_video_media
)
from .utility import check_files_types, check_video

from src.channels.utility import get_current_channel
from src.database import session_dep
from src.auth.dependencies import user_dep
from src.limiter import limiter


videos_router = APIRouter(prefix="/videos")


@videos_router.post("/", status_code=201, response_model=VideoSchema)
@limiter.limit("5/minute")
async def upload_video(
    request: Request, 
    session: session_dep, 
    user: user_dep,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    channel_id: Annotated[int, Form()],
    video_file: UploadFile = File(...),
    cover_file: UploadFile = File(...)
):
    """Controller to upload video to user channel"""
    # getting user channel
    await get_current_channel(session, user, channel_id)
    # checking files types 
    check_files_types(video_file, cover_file)
    # saving video and cover files
    video_file_path, video_filename = await save_file(video_file, user.id)
    cover_file_path, cover_filename = await save_file(cover_file, user.id)
  
    # creating video with media
    try:
        video_data = VideoCreateInternal(
            name=name,
            description=description,
            channel_id=channel_id,
            user_id=user.id,
            video_file_path=video_file_path,
            video_filename=video_filename,
            cover_file_path=cover_file_path,
            cover_filename=cover_filename,
            video_content_type=video_file.content_type,
            cover_content_type=cover_file.content_type
        )
        
        new_video = await create_video_with_media(session, video_data)
    except Exception:
        # handling errors
        delete_file(video_file_path)
        delete_file(cover_file_path)

        await session.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create video in database"
        )
            
    return VideoSchema.model_validate(new_video)
    

@videos_router.get("/", status_code=200, response_model=List[VideoLazySchema])
@cache(expire=60)
async def videos(
    request: Request, 
    session: session_dep, 
    user: user_dep, 
    page: int = Query(1, gt=0),
    search: str | None = Query(None, min_length=1, max_length=100)
):
    """Controller to get videos list with pagination and optional search"""
    video_list = [
        VideoLazySchema.model_validate(video) for video in await get_videos(session, page, search=search)
    ]
    
    return video_list


@videos_router.get("/{video_id}/", status_code=200, response_model=VideoSchema)
@cache(expire=60)
async def video(request: Request, session: session_dep, user: user_dep, video_id: int):
    """Controller to get video by id"""
    video = await get_video(session, video_id)

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    return VideoSchema.model_validate(video)


@videos_router.post("/download/{media_id}/", status_code=200, response_class=FileResponse)
@limiter.limit("10/minute")
async def download_media(request: Request, session: session_dep, user: user_dep, media_id: int):
    """Controller to download video media"""
    media = await get_media(session, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
        
    if not os.path.exists(media.file_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Media file not found"
        )
       
    return FileResponse(media.file_path, filename=Path(media.file_path).name, media_type=media.media_type)


@videos_router.patch("/{video_id}/media/", status_code=200)
@limiter.limit("5/minute")
async def video_update_media(   
    request: Request,                         
    session: session_dep, 
    user: user_dep,
    video_id : int,
    video_file: Optional[UploadFile] = File(default=None),
    cover_file: Optional[UploadFile] = File(default=None)
) -> dict: 
    """Controller to update video media"""
    video = await get_video(
        session, 
        video_id=video_id, 
        load_channel=True,
        load_cover_media=True if cover_file is not None else False, 
        load_video_media=True if video_file is not None else False
    )
    check_video(video, user)
    
    if not await update_video_media(
        session=session,
        cover_file=cover_file,
        video_file=video_file,
        video=video,
        user_id=user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Video media not found"
        )

    return {"detail": "Your video media was updated"}


@videos_router.patch("/{video_id}/", status_code=200)
@limiter.limit("15/minute")
async def video_update(
    request: Request,    
    session: session_dep, 
    user: user_dep,
    video_data: VideoUpdateSchema,
    video_id : int
) -> dict: 
    """Controller to update video"""
    video = await get_video(session, video_id, load_channel=True)
    
    check_video(video, user)
    
    await update_video(
        session, 
        video, 
        video_data
    )
   
    return {"detail": "Your video was updated"}


@videos_router.delete("/{video_id}/", status_code=200)
async def video_delete(request: Request, session: session_dep, user: user_dep, video_id: int):
    """Controller to delete video"""
    video = await get_video(
        session, 
        video_id,
        load_channel=True,
        load_cover_media=True,
        load_video_media=True
    )
    
    check_video(video, user)
    
    if not await delete_video_with_media(session, video):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video"
        )
    
    return {"detail": "Video have been successfully deleted"}
