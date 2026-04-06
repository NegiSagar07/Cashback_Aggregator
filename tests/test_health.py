import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_database_health(client: AsyncClient):
    response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "reachable"
