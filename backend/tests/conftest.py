import tempfile
from pathlib import Path
from io import BytesIO

import pytest
import pytest_asyncio
from fastapi import UploadFile
from httpx import ASGITransport, AsyncClient

from .fake_db import engine, new_session

from src.config import settings
from src.database import get_session

from src.main import app
from src.models import Base, User, Channel

from src.auth.jwt_handler import create_access_token
from src.auth.auth import hash_password

from src.videos.crud import create_video_with_media
from src.videos.schemas import VideoCreateInternal
from src.videos.media_handler import save_file


base_url = f"http://localhost:8000{settings.prefix}/"


@pytest_asyncio.fixture(scope="function")
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with new_session() as db_session:
        yield db_session
            
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(session):    
    async def override_get_db():
        yield session
    
    app.dependency_overrides[get_session] = override_get_db
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url=base_url) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def user(session):    
    user = User(username="test", password=hash_password("test"))
    
    session.add(user)
    await session.commit()
    
    yield user
       
        
@pytest_asyncio.fixture(scope="function")
async def auth_client(client, user):
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client
    

@pytest_asyncio.fixture(scope="function")
async def auth_client_no_channel(session, client):
    user = User(username="someUsername", password=hash_password("test"))
    
    session.add(user)
    await session.commit()
    
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client


@pytest_asyncio.fixture(scope="function")
async def channel(session, user):
    channel = Channel(user_id=user.id, name="channel", description="channel description")
    
    session.add(channel)
    await session.commit()
    
    yield channel


@pytest.fixture
def temp_media_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr(settings, "media_path", Path(temp_dir))
        
        yield Path(temp_dir)


@pytest.fixture
def video_file():
    return ("video.png", BytesIO(b"fake video content"), "video/mp4")


@pytest.fixture
def cover_file():
    return ("cover.png", BytesIO(b"fake cover content"), "image/png")


@pytest_asyncio.fixture(scope="function")
async def video(session, user, channel, temp_media_dir):
    video_content = BytesIO(b"fake video content")
    video_file = UploadFile(
        file=video_content,
        size=len(b"fake video content"),
        filename="video.mp4",
        headers={"content-type": "video/mp4"}
    )
    
    cover_content = BytesIO(b"fake cover content")
    cover_file = UploadFile(
        file=cover_content,
        size=len(b"fake cover content"),
        filename="cover.png",
        headers={"content-type": "image/png"}
    )
    
    video_file_path, video_filename = await save_file(video_file, user.id)
    cover_file_path, cover_filename = await save_file(cover_file, user.id)
    
    video_data = VideoCreateInternal(
        name="name",
        description="description",
        channel_id=channel.id,
        user_id=user.id,
        video_file_path=video_file_path,
        video_filename=video_filename,
        cover_file_path=cover_file_path,
        cover_filename=cover_filename,
        video_content_type=video_file.content_type,
        cover_content_type=cover_file.content_type
    )

    video = await create_video_with_media(session, video_data)
        
    yield video
