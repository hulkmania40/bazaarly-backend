import pytest
from uuid import UUID, uuid5, NAMESPACE_DNS
from app.models.order import Order, OrderItem, OrderStatus
from decimal import Decimal
from datetime import datetime, timezone


def _uid(seed: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"bazaarly:{seed}")


@pytest.mark.asyncio
async def test_customer_orders_mine(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get("/api/v1/orders/mine", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_seller_orders_mine(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "seller@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get("/api/v1/orders/seller/mine", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_order_detail(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get(f"/api/v1/orders/{_uid('order:1')}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
