import pytest


@pytest.mark.asyncio
async def test_get_coupons_returns_empty_list(client):
    response = await client.get("/coupons")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert payload.get("coupons") == []
