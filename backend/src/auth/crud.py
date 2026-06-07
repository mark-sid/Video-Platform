from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .auth import hash_password
from src.models import User


async def get_user(session: AsyncSession, username: str = None) -> Optional[User]:
    """Function to get user by username"""
    if not username:
        return None
    
    stmt = select(User).where(
        User.username == username
    ).options(selectinload(User.channels))
        
    user = await session.execute(stmt)
        
    return user.scalars().first()


async def create_user(session: AsyncSession, username: str, password: str) -> User:
    """Function to create new user"""
    new_user = User(
        username=username,
        password=hash_password(password)
    )

    session.add(new_user)
    await session.commit()

    return new_user
