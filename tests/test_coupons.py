from unittest.mock import patch
import pytest
from httpx import AsyncClient
import datetime
from app.models import Coupon

@pytest.mark.asyncio
async def test_get_coupons_empty(client: AsyncClient):
    response = await client.get("/coupons")
    assert response.status_code == 200, response.json()
    payload = response.json()
    assert payload.get("coupons") == []

@pytest.mark.asyncio
async def test_add_coupon(client: AsyncClient):
    fake_coupon = Coupon(
        platform="Amazon",
        discount_type="percentage",
        value=10.0,
        min_spend=50.0,
        max_cap=100.0,
        category="Retail",
        # Use simple string for expiry to avoid serialization issues, as it gets stored in DB.
        # But parse_coupon_from_text returns a Coupon instance with python types. Let's use date.
        expiry=datetime.date(2030, 1, 1)
    )
    fake_coupon.is_active = True
    
    with patch("app.services.coupon_service.parse_coupon_from_text", return_value=fake_coupon):
        response = await client.post("/add-coupon", params={"user_text": "Amazon 10% off"})
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["status"] == "success"
        assert data["saved_coupon"]["platform"] == "Amazon"

@pytest.mark.asyncio
async def test_get_coupons(client: AsyncClient):
    fake_coupon = Coupon(
        platform="Ebay",
        discount_type="fixed",
        value=20.0,
        min_spend=50.0,
        max_cap=None,
        category="Electronics",
        expiry=datetime.date(2030, 1, 1)
    )
    fake_coupon.is_active = True

    with patch("app.services.coupon_service.parse_coupon_from_text", return_value=fake_coupon):
        await client.post("/add-coupon", params={"user_text": "Ebay $20 off"})

    response = await client.get("/coupons")
    assert response.status_code == 200, response.json()
    payload = response.json()
    assert len(payload["coupons"]) >= 1
    # find the created coupon
    assert any(c["platform"] == "Ebay" for c in payload["coupons"])


@pytest.mark.asyncio
async def test_recommend(client: AsyncClient):
    platform = "Flipkart"
    c1 = Coupon(
        platform=platform,
        discount_type="percentage",
        value=10.0,
        min_spend=0.0,
        max_cap=5.0, # max saving 5
        category="E-commerce",
        expiry=datetime.date(2030, 1, 1),
        is_active=True
    )
    c2 = Coupon(
        platform=platform,
        discount_type="fixed",
        value=20.0, # saving 20
        min_spend=10.0,
        max_cap=None,
        category="E-commerce",
        expiry=datetime.date(2030, 1, 1),
        is_active=True
    )
    
    with patch("app.services.coupon_service.parse_coupon_from_text", side_effect=[c1, c2]):
        response = await client.post("/add-coupon", params={"user_text": "Flipkart 10% off"})
        assert response.status_code == 200, response.json()
        response = await client.post("/add-coupon", params={"user_text": "Flipkart 20 off"})
        assert response.status_code == 200, response.json()

    response = await client.get("/recommend", params={"platform": platform, "amount": 100})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["message"] == "Best deal found!"
    assert data["coupon"]["value"] == 20.0  # c2 should be better
    
    response = await client.get("/recommend", params={"platform": "Unknown", "amount": 100})
    assert response.status_code == 200, response.json()
    assert "No valid coupons found" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_coupons_by_category(client: AsyncClient):
    fake_coupon = Coupon(
        platform="Booking.com",
        discount_type="fixed",
        value=50.0,
        min_spend=100.0,
        category="Travel",
        expiry=datetime.date(2030, 1, 1),
        is_active=True
    )
    with patch("app.services.coupon_service.parse_coupon_from_text", return_value=fake_coupon):
        response = await client.post("/add-coupon", params={"user_text": "Travel 50 off"})
        assert response.status_code == 200, response.json()

    response = await client.get("/coupons/by-category", params={"category": "Travel"})
    assert response.status_code == 200, response.json()
    payload = response.json()
    assert len(payload["coupons"]) >= 1
    assert any(c["platform"] == "Booking.com" for c in payload["coupons"])
