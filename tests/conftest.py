import pytest
import pytest_asyncio
from uuid import UUID, uuid5, NAMESPACE_DNS
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.seller import Seller
from app.models.product import Product, ProductStatus
from app.models.order import Order, OrderItem, OrderStatus
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import get_session as _orig_get_session

DATABASE_URL = "postgresql+asyncpg://bazaarly:bazaarly@localhost:5432/bazaarly"


def _uid(seed: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"bazaarly:{seed}")


@pytest_asyncio.fixture(scope="session")
async def _setup_db():
    e = create_async_engine(DATABASE_URL, echo=False, future=True)
    async with e.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield e
    async with e.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await e.dispose()


@pytest_asyncio.fixture
async def session(_setup_db):
    factory = async_sessionmaker(_setup_db, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s


@pytest_asyncio.fixture
async def client(_setup_db):
    factory = async_sessionmaker(_setup_db, class_=AsyncSession, expire_on_commit=False)

    async def _override():
        async with factory() as s:
            yield s

    app.dependency_overrides[_orig_get_session] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def seed_db(session: AsyncSession):
    users = [
        User(id=_uid("user:1"), name="Bazaarly Admin", email="admin@bazaarly.test", password_hash=hash_password("password123"), role=Role.admin),
        User(id=_uid("user:2"), name="Aria Stores", email="seller@bazaarly.test", password_hash=hash_password("password123"), role=Role.seller),
        User(id=_uid("user:3"), name="Nova Crafts", email="seller2@bazaarly.test", password_hash=hash_password("password123"), role=Role.seller),
        User(id=_uid("user:4"), name="Jane Buyer", email="customer@bazaarly.test", password_hash=hash_password("password123"), role=Role.customer),
        User(id=_uid("user:5"), name="Ravi K.", email="customer2@bazaarly.test", password_hash=hash_password("password123"), role=Role.customer),
    ]
    for u in users:
        session.add(u)
    await session.flush()

    s1 = Seller(id=_uid("seller:1"), user_id=users[1].id, store_name="Aria Stores", description="Handmade ceramics", avatar_url="https://example.com/aria.jpg")
    s2 = Seller(id=_uid("seller:2"), user_id=users[2].id, store_name="Nova Crafts", description="Leather goods", avatar_url="https://example.com/nova.jpg")
    for s in [s1, s2]:
        session.add(s)
    await session.flush()

    p1 = Product(id=_uid("product:1"), seller_id=s1.id, title="Ceramic Vase", description="vase", price=Decimal("29.99"), currency="USD", image_url="https://example.com/vase.jpg", status=ProductStatus.approved)
    p2 = Product(id=_uid("product:2"), seller_id=s1.id, title="Clay Mug", description="mug", price=Decimal("14.50"), currency="USD", image_url="https://example.com/mug.jpg", status=ProductStatus.pending)
    for p in [p1, p2]:
        session.add(p)
    await session.flush()
    await session.commit()
