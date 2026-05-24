from fastapi import APIRouter, status, HTTPException
from typing import List

from .crud import get_channels, get_channel, create_channel, update_channel, delete_channel
from .schemas import ChannelSchema, ChannelCreateSchema
from .utility import get_current_channel, check_same_channel_name

from src.auth.dependencies import user_dep
from src.database import session_dep

channels_router = APIRouter(prefix="/channels")


@channels_router.get("/", status_code=200, response_model=List[ChannelSchema])
async def channels(session: session_dep, user: user_dep) -> dict:
    channels_list = [
        ChannelSchema.model_validate(channel) for channel in await get_channels(session)
    ]
    
    return channels_list


@channels_router.post("/", status_code=201, response_model=ChannelSchema)
async def start_channel(session: session_dep, channel_data: ChannelCreateSchema, user: user_dep) -> dict:
    await check_same_channel_name(session, channel_data.name)

    new_channel = await create_channel(
        session,
        user.id, 
        channel_data.name, 
        channel_data.description
    )          
    
    
    return ChannelSchema.model_validate(new_channel)
                         
    
    
@channels_router.put("/", status_code=200)
async def channel_update(session: session_dep, channel_data: ChannelSchema, user: user_dep) -> dict: 
    channel = await get_current_channel(session, user, channel_data.id)
    
    if channel.name != channel_data.name:
        await check_same_channel_name(session, channel_data.name)

    await update_channel(
        session, channel, channel_data.name, channel_data.description
    )
   
    return {"detail": "Your channel was updated"}
                                                                                   
                                                                        
@channels_router.get("/{channel_id}/", status_code=200, response_model=ChannelSchema)
async def channel_get(channel_id: int, session: session_dep, user: user_dep) -> dict:    
    channel = await get_channel(session, id=channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid channel id"
        )
    
    return ChannelSchema.model_validate(channel)
              
    
                                                        
@channels_router.delete("/{channel_id}/", status_code=200)
async def channel_delete(channel_id: int, session: session_dep, user: user_dep) -> dict:    
    channel = await get_current_channel(session, user, channel_id)
    
    await delete_channel(session, channel)
    
    return {"detail": "Channel have been successfully deleted"}                                                                        