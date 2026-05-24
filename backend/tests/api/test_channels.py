import pytest
from src.channels.crud import get_channel, create_channel


# test channel create
@pytest.mark.asyncio
@pytest.mark.parametrize(("name", "status"), [("uniqueChannel", 201), ("channel", 409)])
async def test_create_video(auth_client, channel, name, status):
    response = await auth_client.post(
        "/channels/", 
        json={
            "name": name, 
            "description": "test channel description"        
        }
    )

    assert response.status_code == status
    
    if name == "uniqueChannel":
        assert "name" in response.json() 
    else:
        assert response.json() == {"detail": "There is already a channel with same name"}
    

# test get channels
@pytest.mark.asyncio
async def test_get_channels_successful(auth_client, channel):
    response = await auth_client.get(
        "/channels/"
    )

    assert response.status_code == 200
    assert "name" in response.json()[0]
    

# test get channel by id
@pytest.mark.asyncio
async def test_get_channel_successful(auth_client, channel):
    response = await auth_client.get(
        f"/channels/{channel.id}/"
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": channel.name,
        "description": channel.description,
        "id": channel.id
    }
 
 
@pytest.mark.asyncio
async def test_get_channel_wrong_id(auth_client, channel):
    response = await auth_client.get(
        f"/channels/{channel.id + 1}/" # there is no channel in db with id greater than id of channel created in fixture
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid channel id"}
    
    
# test update channel
@pytest.mark.asyncio
async def test_update_channel_successful(session, auth_client, channel):
    response = await auth_client.put(
        "/channels/",
        json={
            "id": channel.id,
            "name": "funny channel",
            "description": channel.description    
        }
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Your channel was updated"}
    
    await session.refresh(channel)
    
    assert channel.name == "funny channel"


@pytest.mark.asyncio
async def test_update_channel_name_already_exists(session, auth_client, channel, user):    
    await create_channel(session, user.id, "name_exists", "description")
    
    response = await auth_client.put(
        "/channels/",
        json={
            "id": channel.id,
            "name": "name_exists",
            "description": channel.description    
        }
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "There is already a channel with same name"}


# test delete channel
@pytest.mark.asyncio
async def test_delete_channel(session, auth_client, channel):
    response = await auth_client.delete(
        f"/channels/{channel.id}/",
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Channel have been successfully deleted"} 

    assert await get_channel(session, id=channel.id) is None
    
@pytest.mark.asyncio
async def test_delete_channel_wrong_id(auth_client, channel):
    response = await auth_client.delete(
        f"/channels/{channel.id + 1}/", # there is no channel in db with id greater than id of channel created in fixture
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Channel not found"}
