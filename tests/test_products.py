import pytest
from uuid import UUID, uuid5, NAMESPACE_DNS
from app.models.product import Product, ProductStatus
from app.models.seller import Seller
from decimal import Decimal


def _uid(seed: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"bazaarly:{seed}")


@pytest.mark.asyncio
async def test_admin_list_all_products(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "admin@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get("/api/v1/products", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)


@pytest.mark.asyncio
async def test_seller_my_products(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "seller@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get("/api/v1/products/mine", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_customer_cannot_create_product(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {token}"}, json={"title": "New", "description": "desc", "price": 10.00, "image_url": "url"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_product_sets_pending(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "seller@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.post("/api/v1/products", headers={"Authorization": f"Bearer {token}"}, json={"title": "New Ceramic", "description": "handmade", "price": 25.00, "image_url": "https://example.com/pic.jpg"})
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_product_detail_approved(client, session):
    await seed_db(session)
    login = await client.post("/api/v1/auth/login", json={"email": "customer@bazaarly.test", "password": "password123"})
    token = login.json()["access_token"]
    resp = await client.get(f"/api/v1/products/{_uid('product:1')}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Ceramic Vase"
