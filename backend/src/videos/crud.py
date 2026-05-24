import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
from typing import Optional, List

from src.config import settings
from src.models import Video, Media
from .schemas import VideoUpdateShema, VideoCreateInternal
from .media_handler import save_file, delete_file
from .utility import check_file_type


# ===============================
# Video block
# ===============================
async def create_video(
    session: AsyncSession,
    name: str,  
    description: str, 
    channel_id: int,
    video_media_id: int,
    cover_media_id: int
) -> Video:
    try:
        video = Video(
            name=name, 
            description=description, 
            channel_id=channel_id, 
            video_media_id=video_media_id, 
            cover_media_id=cover_media_id
        )
        
        session.add(video)
        
        await session.commit()
    
        
        return video

    except Exception:
        await session.rollback()
        raise
    

async def get_video(
    session: AsyncSession,
    video_id: int,
    load_channel=False,
    load_video_media=False,
    load_cover_media=False
) -> Optional[Video]:
    if not video_id:
        return None
    
    stmt = select(Video).where(Video.id == video_id)
    
    if load_channel:
        stmt = stmt.options(selectinload(Video.channel))
        
    if load_video_media:
        stmt = stmt.options(selectinload(Video.video_media))
        
    if load_cover_media:    
        stmt = stmt.options(selectinload(Video.cover_media))        

    video = await session.execute(stmt)

    return video.scalar_one_or_none()


async def get_videos(session: AsyncSession, page: int = 1) -> List[Video]:
    offset = (page - 1) * 40 # per_page is a constant value of 40
    
    videos = await session.execute(
        select(
            Video.id, 
            Video.name, 
            Video.description, 
            Video.cover_media_id
        ).offset(offset).limit(40)     
    )
    
    return videos.all()


async def update_video(session: AsyncSession, video: Video, video_data: VideoUpdateShema) -> None:
    if video:
        to_update = video_data.model_dump(exclude_unset=True)
        
        for key, value in to_update.items():
            setattr(video, key, value)
            
        await session.commit()
    
    return None
    
    
async def delete_video(session: AsyncSession, video: Video) -> bool:
    if not video:
        return False
    
    await session.delete(video)
    await session.commit()
        
    return True


# ===============================
# Media block
# ===============================
async def get_media(session: AsyncSession, media_id) -> Optional[Media]:
    if not media_id:
        return None
    
    stmt = select(Media).where(Media.id == media_id)        

    media = await session.execute(stmt)

    return media.scalar_one_or_none()



async def create_media(session: AsyncSession, filename: str, file_path: str, media_type: str) -> Media:
    media = Media(
        filename=filename, 
        file_path=file_path, 
        media_type=media_type
    )
       
    session.add(media)
    await session.commit()
    
    return media


async def update_media(session: AsyncSession, id: int, filename: str, file_path: str):
    media = await get_media(session, id)
    
    if not media:
        return False
    
    media.filename = filename
    media.file_path  = file_path
        
    await session.commit()
        
    return True
    


async def update_video_media(
    session: AsyncSession, 
    cover_file: UploadFile, 
    video_file: UploadFile,
    video: Video,
    user_id: int
    
) -> bool:
    if cover_file:            
        check_file_type(cover_file, settings.ALLOWED_COVER_MEDIA_TYPES)
        cover_file_path, cover_filename = await save_file(cover_file, user_id)
        delete_file(video.cover_media.file_path)
        
        if not await update_media(
            session,
            video.cover_media_id,
            cover_filename,
            cover_file_path,
        ): 
            return False
        
    # update video media if video file is given
    if video_file:
        check_file_type(video_file, settings.ALLOWED_VIDEO_MEDIA_TYPES)
                
        video_file_path, video_filename = await save_file(video_file, user_id)  
        
        delete_file(video.video_media.file_path)
        
        if not await update_media(
            session,
            video.video_media_id,
            video_filename,
            video_file_path
        ):
            return False
    
    return True
    
    
# ===============================
# Video + Media block
# ===============================
async def create_video_with_media(session: AsyncSession, video_data: VideoCreateInternal) -> Video:
    video_media = await create_media(
        session, 
        video_data.video_filename, 
        video_data.video_file_path, 
        video_data.video_content_type
    )
    cover_media = await create_media(
        session, 
        video_data.cover_filename, 
        video_data.cover_file_path, 
        video_data.cover_content_type
    )
    # creating video object 
    new_video = await create_video(
        session, 
        video_data.name,
        video_data.description,
        video_data.channel_id,  
        video_media.id, 
        cover_media.id     
    )
    
    return new_video


async def delete_video_with_media(session: AsyncSession, video: Video) -> bool:
    if not video:
        return False
        
    try:
        delete_file(video.cover_media.file_path)
        delete_file(video.video_media.file_path)
    except FileNotFoundError:
        return False
        
    if not await delete_video(session, video):
        return False
        
    return True
    
    