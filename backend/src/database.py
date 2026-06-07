from typing import Annotated


from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from src.config import settings

engine = create_async_engine(
    settings.database_url,
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_session():
    async with new_session() as session:
        yield session

session_dep = Annotated[AsyncSession, Depends(get_session)]
