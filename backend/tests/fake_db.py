from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings

engine = create_async_engine(
    settings.test_database_url
)

new_session = async_sessionmaker(engine, expire_on_commit=False)
