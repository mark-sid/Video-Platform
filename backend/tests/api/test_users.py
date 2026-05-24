import pytest

# test user create
@pytest.mark.asyncio
async def test_user_create_successful(client):
    response = await client.post(
        "/user/", 
        json={
            "username": "uniqueUsername", 
            "password": "test", 
            "password_repeat": "test"
        }
    )

    assert response.status_code == 201
    assert response.json()["username"] == "uniqueUsername"
    
    
@pytest.mark.asyncio
async def test_user_create_username_already_exists(client, user):
    response = await client.post(
        "/user/", 
        json={
            "username": "test", # This username is already taken by user created in fixture 
            "password": "test", 
            "password_repeat": "test"
        }
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


@pytest.mark.asyncio
async def test_user_create_validation_error(client):
    response = await client.post(
        "/user/", 
        json={
            "username": "username", 
            "password": "password", 
            "password_repeat": "wrong_passowrd"
        }
    )

    assert response.status_code == 422
    assert "detail" in response.json()  
    
    
# test user login
@pytest.mark.asyncio
@pytest.mark.parametrize("password, status", [("test", 200), ("incorrect_password", 401)])
async def test_login(client, user, password, status):
    response = await client.post(
        "/user/token/", 
        data={
            "username": "test", 
            "password": password, 
        }
    )

    assert response.status_code == status
    
    if password == "test":
        assert "access_token" in response.json()  
    else:
        assert response.json() == {"detail": "Incorrect username or password"}  
1
    