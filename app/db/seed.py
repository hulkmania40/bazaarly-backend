import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_DNS
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.user import User, Role
from app.models.seller import Seller
from app.models.product import Product, ProductStatus
from app.models.order import Order, OrderItem
from app.core.security import hash_password


def _uid(seed: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"bazaarly:{seed}")


USERS = [
    User(id=_uid("user:1"), name="Bazaarly Admin", email="admin@bazaarly.test", password_hash=hash_password("password123"), role=Role.admin),
    User(id=_uid("user:2"), name="Aria Stores", email="seller@bazaarly.test", password_hash=hash_password("password123"), role=Role.seller),
    User(id=_uid("user:3"), name="Nova Crafts", email="seller2@bazaarly.test", password_hash=hash_password("password123"), role=Role.seller),
    User(id=_uid("user:4"), name="Jane Buyer", email="customer@bazaarly.test", password_hash=hash_password("password123"), role=Role.customer),
    User(id=_uid("user:5"), name="Ravi K.", email="customer2@bazaarly.test", password_hash=hash_password("password123"), role=Role.customer),
]

ADMIN_ID = _uid("user:1")
SELLER1_ID = _uid("user:2")
SELLER2_ID = _uid("user:3")
CUST1_ID = _uid("user:4")
CUST2_ID = _uid("user:5")

SELLERS = [
    Seller(id=_uid("seller:1"), user_id=SELLER1_ID, store_name="Aria Stores", description="Handmade ceramics & home goods", avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100"),
    Seller(id=_uid("seller:2"), user_id=SELLER2_ID, store_name="Nova Crafts", description="Minimalist leather goods", avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100"),
]

SELLER1 = SELLERS[0]
SELLER2 = SELLERS[1]

def _p(seed: str, seller_id: UUID, title: str, desc: str, price: str, img: str, status: str, reason: str | None = None) -> dict:
    return {
        "id": _uid(f"product:{seed}"),
        "seller_id": seller_id,
        "title": title,
        "description": desc,
        "price": Decimal(price),
        "currency": "USD",
        "image_url": img,
        "status": status,
        "rejection_reason": reason,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

APPROVED = [
    _p("p1", SELLER1.id, "Ceramic Vase", "Handcrafted ceramic vase", "29.99", "https://images.unsplash.com/photo-1578500492678-8b9b97e67149?w=300", ProductStatus.approved),
    _p("p2", SELLER1.id, "Clay Mug", "Handmade clay mug", "14.50", "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=300", ProductStatus.approved),
    _p("p3", SELLER1.id, "Terracotta Planter", "Small terracotta planter", "19.00", "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=300", ProductStatus.approved),
    _p("p4", SELLER1.id, "Dinner Plate Set", "Set of 4 dinner plates", "49.99", "https://images.unsplash.com/photo-1578749556935-41057a17090d?w=300", ProductStatus.approved),
    _p("p5", SELLER1.id, "Serving Bowl", "Large serving bowl", "34.00", "https://images.unsplash.com/photo-1590794056226-79ef3aef7e6b?w=300", ProductStatus.approved),
    _p("p6", SELLER1.id, "Espresso Cup", "Small espresso cup", "12.00", "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=200", ProductStatus.approved),
    _p("p7", SELLER2.id, "Leather Wallet", "Minimalist leather wallet", "59.00", "https://images.unsplash.com/photo-1627123424574-724758594e93?w=300", ProductStatus.approved),
    _p("p8", SELLER2.id, "Leather Belt", "Handcrafted leather belt", "39.00", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300", ProductStatus.approved),
    _p("p9", SELLER2.id, "Leather Notebook Cover", "A5 notebook cover", "24.00", "https://images.unsplash.com/photo-1544816155-12df9643f363?w=300", ProductStatus.approved),
    _p("p10", SELLER2.id, "Card Holder", "Slim card holder", "18.00", "https://images.unsplash.com/photo-1627123424574-724758594e93?w=200", ProductStatus.approved),
    _p("p11", SELLER2.id, "Leather Keychain", "Handmade keychain", "15.00", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=200", ProductStatus.approved),
    _p("p12", SELLER2.id, "Watch Strap", "Handstitched leather strap", "45.00", "https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=300", ProductStatus.approved),
]

PENDING = [
    _p("p13", SELLER1.id, "Glazed Bowl", "Glazed ceramic bowl", "22.00", "https://images.unsplash.com/photo-1578500492678-8b9b97e67149?w=300", ProductStatus.pending),
    _p("p14", SELLER1.id, "Raku Pot", "Raku fired pot", "55.00", "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=300", ProductStatus.pending),
    _p("p15", SELLER1.id, "Tea Set", "4-piece tea set", "65.00", "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=300", ProductStatus.pending),
    _p("p16", SELLER1.id, "Lamp Base", "Ceramic lamp base", "42.00", "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=300", ProductStatus.pending),
    _p("p17", SELLER1.id, "Butter Dish", "Ceramic butter dish", "16.00", "https://images.unsplash.com/photo-1590794056226-79ef3aef7e6b?w=200", ProductStatus.pending),
    _p("p18", SELLER2.id, "Tote Bag", "Leather tote bag", "89.00", "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=300", ProductStatus.pending),
    _p("p19", SELLER2.id, "Leather Glasses Case", "Protective glasses case", "28.00", "https://images.unsplash.com/photo-1544816155-12df9643f363?w=200", ProductStatus.pending),
]

REJECTED = [
    _p("p20", SELLER1.id, "Broken Bowl", "Damaged bowl", "10.00", "https://images.unsplash.com/photo-1578500492678-8b9b97e67149?w=300", ProductStatus.rejected, "Item is damaged"),
    _p("p21", SELLER2.id, "Fake Leather", "Not real leather", "25.00", "https://images.unsplash.com/photo-1627123424574-724758594e93?w=300", ProductStatus.rejected, "Not genuine leather"),
    _p("p22", SELLER2.id, "Poor Quality", "Low quality item", "20.00", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300", ProductStatus.rejected, "Poor craftsmanship"),
]

ALL_PRODUCTS = APPROVED + PENDING + REJECTED

ORDERS = [
    Order(id=_uid("order:1"), customer_id=CUST1_ID, seller_id=SELLER1.id, total=Decimal("44.49"), currency="USD", status=OrderStatus.pending, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
    Order(id=_uid("order:2"), customer_id=CUST1_ID, seller_id=SELLER2.id, total=Decimal("77.00"), currency="USD", status=OrderStatus.paid, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
    Order(id=_uid("order:3"), customer_id=CUST2_ID, seller_id=SELLER1.id, total=Decimal("29.99"), currency="USD", status=OrderStatus.accepted, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
    Order(id=_uid("order:4"), customer_id=CUST2_ID, seller_id=SELLER2.id, total=Decimal("59.00"), currency="USD", status=OrderStatus.out_for_delivery, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
    Order(id=_uid("order:5"), customer_id=CUST1_ID, seller_id=SELLER1.id, total=Decimal("14.50"), currency="USD", status=OrderStatus.delivered, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)),
]

OIS = [
    OrderItem(id=_uid("oi:1"), order_id=ORDERS[0].id, product_id=APPROVED[0]["id"], title="Ceramic Vase", price=Decimal("29.99"), quantity=1, image_url=APPROVED[0]["image_url"]),
    OrderItem(id=_uid("oi:2"), order_id=ORDERS[0].id, product_id=APPROVED[1]["id"], title="Clay Mug", price=Decimal("14.50"), quantity=1, image_url=APPROVED[1]["image_url"]),
    OrderItem(id=_uid("oi:3"), order_id=ORDERS[1].id, product_id=APPROVED[6]["id"], title="Leather Wallet", price=Decimal("59.00"), quantity=1, image_url=APPROVED[6]["image_url"]),
    OrderItem(id=_uid("oi:4"), order_id=ORDERS[1].id, product_id=APPROVED[7]["id"], title="Leather Belt", price=Decimal("18.00"), quantity=1, image_url=APPROVED[7]["image_url"]),
    OrderItem(id=_uid("oi:5"), order_id=ORDERS[2].id, product_id=APPROVED[0]["id"], title="Ceramic Vase", price=Decimal("29.99"), quantity=1, image_url=APPROVED[0]["image_url"]),
    OrderItem(id=_uid("oi:6"), order_id=ORDERS[3].id, product_id=APPROVED[6]["id"], title="Leather Wallet", price=Decimal("59.00"), quantity=1, image_url=APPROVED[6]["image_url"]),
    OrderItem(id=_uid("oi:7"), order_id=ORDERS[4].id, product_id=APPROVED[1]["id"], title="Clay Mug", price=Decimal("14.50"), quantity=1, image_url=APPROVED[1]["image_url"]),
]


async def seed():
    engine = create_async_engine("postgresql+asyncpg://bazaarly:bazaarly@localhost:5432/bazaarly", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as session:
        for u in USERS:
            session.add(u)
        for s in SELLERS:
            session.add(s)
        for p in ALL_PRODUCTS:
            session.add(Product(**p))
        for o in ORDERS:
            session.add(o)
        for oi in OIS:
            session.add(oi)
        await session.commit()

    await engine.dispose()
    print("Seed complete: 5 users, 2 sellers, 22 products, 5 orders, 7 order items.")


if __name__ == "__main__":
    asyncio.run(seed())
