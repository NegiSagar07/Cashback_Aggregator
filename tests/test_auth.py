import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "new_test_user",
        "password": "securepassword123"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_test_user"
    assert "id" in data
    
    # Try duplicate registration
    response_dup = await client.post("/auth/register", json={
        "username": "new_test_user",
        "password": "securepassword123"
    })
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient):
    await client.post("/auth/register", json={
        "username": "login_user",
        "password": "securepassword123"
    })
    
    response = await client.post(
        "/auth/token", 
        data={"username": "login_user", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    response = await client.post(
        "/auth/token", 
        data={"username": "login_user", "password": "wrongpassword"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_read_current_user(client: AsyncClient):
    response = await client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user"
