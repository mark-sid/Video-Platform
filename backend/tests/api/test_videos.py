import pytest
from io import BytesIO
from src.videos.crud import get_media, get_video


# test video create
@pytest.mark.asyncio
async def test_create_successful(auth_client, channel, video_file, cover_file, temp_media_dir):
    response = await auth_client.post(
        "/videos/", 
        data={
            "name": "name",
            "description": "description",
            "channel_id": channel.id,    
        },
        files={
            "video_file": video_file,
            "cover_file": cover_file
        }
    )

    assert response.status_code == 201
    assert "name" in response.json()


@pytest.mark.asyncio
async def test_create_wrong_channel_id(auth_client, channel, video_file, cover_file):
    response = await auth_client.post(
        "/videos/", 
        data={
            "name": "name",
            "description": "description",
            "channel_id": channel.id + 1, # Incorrect channel id 
        },
        files={
            "video_file": video_file,
            "cover_file": cover_file
        }
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Channel not found"}


@pytest.mark.asyncio
async def test_create_wrong_channel_user(auth_client_no_channel, channel, video_file, cover_file):    
    response = await auth_client_no_channel.post(
        "/videos/", 
        data={
            "name": "name",
            "description": "description",
            "channel_id": channel.id,    
        },
        files={
            "video_file": video_file,
            "cover_file": cover_file
        }
    )
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied"}


@pytest.mark.asyncio
async def test_create_wrong_file_type(auth_client, cover_file, channel):
    response = await auth_client.post(
        "/videos/", 
        data={
            "name": "name",
            "description": "description",
            "channel_id": channel.id,    
        },
        files={
            "video_file": cover_file, # wrong file
            "cover_file": cover_file
        }
    )
    
    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported type of file was given"}
    
    
# test get video list
@pytest.mark.asyncio
@pytest.mark.parametrize(("page, status"), [(1, 200), (-1, 422)])
async def test_video_list(auth_client, video, page, status):
    response = await auth_client.get(
        f"/videos/?page={page}" 
    )
    
    assert response.status_code == status
    
    if page == 1:
        assert response.json()[0]["id"] == video.id
    

# test get video by id
@pytest.mark.asyncio
async def test_get_video(auth_client, video):
    response = await auth_client.get(
        f"/videos/{video.id}/",
    )
    
    assert response.status_code == 200
    assert video.name in response.json()


@pytest.mark.asyncio
async def test_get_video_wrong_id(auth_client, video):
    response = await auth_client.get(
        f"/videos/{video.id + 1}/", # there is no video in db with id greater than id of video created in fixture
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Video not found"}

# test media download
@pytest.mark.asyncio
async def test_cover_download(auth_client, video):    
    response = await auth_client.post(
        f"/videos/download/{video.cover_media_id}/"
    )
    
    assert response.status_code == 200
    assert "image/png" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_video_download(auth_client, video, temp_media_dir):    
    response = await auth_client.post(
        f"/videos/download/{video.video_media_id}/"
    )
    
    assert response.status_code == 200
    assert "video/mp4" in response.headers.get("content-type", "")
    
    
@pytest.mark.asyncio
async def test_cover_download_wrong_id(auth_client, video):    
    response = await auth_client.post(
        f"/videos/download/{video.cover_media_id + 1}/" # there is no media in db with id greater than id of video created in fixture
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Media not found"}


@pytest.mark.asyncio
async def test_video_download_wrong_id(auth_client, video):    
    response = await auth_client.post(
        f"/videos/download/{video.video_media_id + 2}/" # + 2 because cover created later and have id == video.video_media_id + 1
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Media not found"}
    
    
# test video media update
@pytest.mark.asyncio
async def test_video_media_update_successful(session, auth_client, video, temp_media_dir):
    response = await auth_client.patch(
        f"/videos/{video.id}/media/", 
        files={
            "video_file": ("updated_video.mp4", BytesIO(b"fake video content"), "video/mp4"),
            "cover_file": ("updated_cover.jpeg", BytesIO(b"fake cover content"), "image/png")
        }
    )
    
    assert response.status_code == 200
    assert response.json() ==  {"detail": "Your video media was updated"}
    
    
    video_media =  await get_media(session, video.video_media_id)
    cover_media = await get_media(session, video.cover_media_id)
    
    assert "updated_cover" in cover_media.filename
    assert "updated_video" in video_media.filename
    
    
@pytest.mark.asyncio
async def test_video_media_update_wrong_id(auth_client, video, cover_file):
    response = await auth_client.patch(
        f"/videos/{video.id + 1}/media/", # there is no video in db with id greater than id of video created in fixture
        files={
            "cover_file": cover_file
        }
    )
    
    assert response.status_code == 404
    assert response.json() ==  {"detail": "Video not found"}


@pytest.mark.asyncio
async def test_video_media_update_access_denied(auth_client_no_channel, video, cover_file):
    response = await auth_client_no_channel.patch(
        f"/videos/{video.id}/media/",
        files={
            "cover_file": cover_file
        }
    )
    
    assert response.status_code == 403
    assert response.json() ==  {"detail": "Access denied"}

    
# test video data update
@pytest.mark.asyncio
async def test_video_update_successful(session, auth_client, video):
    response = await auth_client.patch(
        f"/videos/{video.id}/",
        json={
            "name": "Good video name"
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"detail": "Your video was updated"}
    
    result = await get_video(session, video.id)
    
    assert result.name == "Good video name"
    

@pytest.mark.asyncio
async def test_video_update_wrnog_id(auth_client, video):
    response = await auth_client.patch(
        f"/videos/{video.id + 1}/", # there is no video in db with id greater than id of video created in fixture
        json={
            "name": "Good video name"
        }
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Video not found"}
    

@pytest.mark.asyncio
async def test_video_update_access_denied(auth_client_no_channel, video):
    response = await auth_client_no_channel.patch(
        f"/videos/{video.id}/",
        json={
            "name": "Good video name"
        }
    )
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied"}
    

# test video delete 
@pytest.mark.asyncio
async def test_video_delete_successful(session, auth_client, video, temp_media_dir):
    response = await auth_client.delete(
        f"/videos/{video.id}/",
    )
    
    assert response.status_code == 200
    assert response.json() == {"detail": "Video have been successfully deleted"}
    
    result = await get_video(session, video_id=video.id)
    
    assert result is None
    
    
@pytest.mark.asyncio
async def test_video_delete_wrong_id(auth_client, video):
    response = await auth_client.delete(
        f"/videos/{video.id + 1}/", # there is no video in db with id greater than id of video created in fixture
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Video not found"}

   
@pytest.mark.asyncio
async def test_video_delete_access_denied(auth_client_no_channel, video):
    response = await auth_client_no_channel.delete(
        f"/videos/{video.id}/",
    )
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied"} 
    
