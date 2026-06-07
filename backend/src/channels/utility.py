from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import get_channel

from src.models import Channel, User


async def get_current_channel(session: AsyncSession, user: User, channel_id: int) -> Channel:
    """Function for getting chanell and checking its existing, user access to it"""
    channel = await get_channel(session, id=channel_id)
    
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found") 
       
    if channel.user != user:
        raise HTTPException(status_code=403, detail="Access denied")
       
    return channel
    

async def check_same_channel_name(session: AsyncSession, name: str) -> None:
    """Function to check uniqueness of the channel name"""
    if await get_channel(session, name) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a channel with same name"
        ) 
