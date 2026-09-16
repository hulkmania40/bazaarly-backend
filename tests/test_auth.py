import pytest
from uuid import UUID, uuid5, NAMESPACE_DNS
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.seller import Seller
from app.models.product import Product, ProductStatus
from decimal import Decimal


def _uid(seed: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"bazaarly:{seed}")


@pytest.mark.asyncio
async def test_register_new_user(client, session):
    resp = await client.post("/api/v1/auth/register", json={"name": "Test User", "email": "new@bazaarly.test", "password": "testpass123", "role": "customer"})
    assert resp.status_code == 201
    assert resp.json()["user"]["email"] == "new@bazaarly.test"


@pytest.mark.asyncio
async def test_register_duplicate_email(client, session):
    await seed_db(session)
    resp = await client.post("/api/v1/auth/register", json={"name": "Test", "email": "customer@bazaarly.test", "password": "testpass", "role": "customer"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client, session):
    await seed_db(session)
    resp = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "customer@bazaarly.test"


@pytest.mark.asyncio
async def test_login_wrong_password(client, session):
    await seed_db(session)
    resp = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "wrongpass"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_user(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "customer@bazaarly.test"
