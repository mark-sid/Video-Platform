from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional

from src.config import settings
   
   
class VideoUpdateSchema(BaseModel):
    """Schema for video data updating"""
    name: Optional[str] = None
    description: Optional[str] = None
    
       
class VideoLazySchema(BaseModel):
    """Schema for video lazy response"""
    id: int
    name: str
    description: str
    cover_media_id: int
    
    model_config = ConfigDict(
        from_attributes=True
    )

    @computed_field
    @property
    def cover_download_url(self) -> str:
        return f"http://localhost:8000{settings.prefix}/videos/download/{self.cover_media_id}/" 


class VideoSchema(VideoLazySchema): 
    """Schema for video"""   
    channel_id: int    
    video_media_id: int
    
    @computed_field
    @property
    def video_download_url(self) -> str:        
        return f"http://localhost:8000{settings.prefix}/videos/download/{self.video_media_id}/"    


class VideoCreateInternal(VideoUpdateSchema):
    """Schema for video creating"""
    channel_id: int
    video_file_path: str
    video_filename: str
    cover_file_path: str
    cover_filename: str
    video_content_type: str
    cover_content_type: str
