from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Channel


async def get_channels(session: AsyncSession) -> List[Channel]:
    """Function to get channels"""
    channels = await session.execute(
        select(Channel)
    )
    return channels.scalars().all()


async def get_channel(session: AsyncSession, name: str | None = None, id: int | None = None) -> Optional[Channel]:
    """Function to get channel by id or name"""
    if name is None and id is None:
        return None

    stmt = select(Channel).options(selectinload(Channel.user))
    
    if id is not None:
        stmt = stmt.where(Channel.id == id)
    else:
        stmt = stmt.where(Channel.name == name)

    result = await session.execute(stmt)
    return result.scalars().first()


async def create_channel(session: AsyncSession, user_id: int, name: str, description: str) -> Channel:
    """Function to create channel"""
    new_channel = Channel(
        name=name,
        user_id=user_id,
        description=description
    )

    session.add(new_channel)
    await session.commit()

    return new_channel


async def update_channel(session: AsyncSession, channel: Channel, name: str, description: str) -> None:
    """Function to update channel"""
    if not channel:
        return None
    
    channel.name = name
    channel.description = description
        
    await session.commit()
            

async def delete_channel(session: AsyncSession, channel: Channel) -> bool:
    """Function to delete channel"""
    if not channel:
        return False
    
    await session.delete(channel)
    await session.commit()
            
    return True
          
    
