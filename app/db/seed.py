from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_DNS
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.models.user import User, Role
from app.models.seller import Seller
from app.models.product import Product, ProductStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.core.security import hash_password
from app.db.session import engine


def _uid(seed: str) -> UUID:
    return uuid5(NAMESPACE_DNS, f"bazaarly:{seed}")


ADMIN_ID = _uid("user:1")
SELLER_USER1_ID = _uid("user:2")
SELLER_USER2_ID = _uid("user:3")
CUST1_ID = _uid("user:4")
CUST2_ID = _uid("user:5")

SELLER1_ID = _uid("seller:1")
SELLER2_ID = _uid("seller:2")

USERS = [
    User(id=ADMIN_ID, name="Bazaarly Admin", email="admin@bazaarly.test", password_hash=hash_password("password123"), role=Role.admin),
    User(id=SELLER_USER1_ID, name="Aria Stores", email="seller@bazaarly.test", password_hash=hash_password("password123"), role=Role.seller),
    User(id=SELLER_USER2_ID, name="Nova Crafts", email="seller2@bazaarly.test", password_hash=hash_password("password123"), role=Role.seller),
    User(id=CUST1_ID, name="Jane Buyer", email="customer@bazaarly.test", password_hash=hash_password("password123"), role=Role.customer),
    User(id=CUST2_ID, name="Ravi K.", email="customer2@bazaarly.test", password_hash=hash_password("password123"), role=Role.customer),
]

SELLERS = [
    Seller(id=SELLER1_ID, user_id=SELLER_USER1_ID, store_name="Aria Stores", description="Handmade ceramics & home goods", avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100"),
    Seller(id=SELLER2_ID, user_id=SELLER_USER2_ID, store_name="Nova Crafts", description="Minimalist leather goods", avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100"),
]

PRODUCTS = [
    Product(id=_uid("product:p1"), seller_id=SELLER1_ID, title="Ceramic Vase", description="Handcrafted ceramic vase", price=Decimal("29.99"), currency="USD", image_url="https://images.unsplash.com/photo-1578500492678-8b9b97e67149?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p2"), seller_id=SELLER1_ID, title="Clay Mug", description="Handmade clay mug", price=Decimal("14.50"), currency="USD", image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p3"), seller_id=SELLER1_ID, title="Terracotta Planter", description="Small terracotta planter", price=Decimal("19.00"), currency="USD", image_url="https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p4"), seller_id=SELLER1_ID, title="Dinner Plate Set", description="Set of 4 dinner plates", price=Decimal("49.99"), currency="USD", image_url="https://images.unsplash.com/photo-1578749556935-41057a17090d?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p5"), seller_id=SELLER1_ID, title="Serving Bowl", description="Large serving bowl", price=Decimal("34.00"), currency="USD", image_url="https://images.unsplash.com/photo-1590794056226-79ef3aef7e6b?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p6"), seller_id=SELLER1_ID, title="Espresso Cup", description="Small espresso cup", price=Decimal("12.00"), currency="USD", image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=200", status=ProductStatus.approved),
    Product(id=_uid("product:p7"), seller_id=SELLER2_ID, title="Leather Wallet", description="Minimalist leather wallet", price=Decimal("59.00"), currency="USD", image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p8"), seller_id=SELLER2_ID, title="Leather Belt", description="Handcrafted leather belt", price=Decimal("39.00"), currency="USD", image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p9"), seller_id=SELLER2_ID, title="Leather Notebook Cover", description="A5 notebook cover", price=Decimal("24.00"), currency="USD", image_url="https://images.unsplash.com/photo-1544816155-12df9643f363?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p10"), seller_id=SELLER2_ID, title="Card Holder", description="Slim card holder", price=Decimal("18.00"), currency="USD", image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?w=200", status=ProductStatus.approved),
    Product(id=_uid("product:p11"), seller_id=SELLER2_ID, title="Leather Keychain", description="Handmade keychain", price=Decimal("15.00"), currency="USD", image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=200", status=ProductStatus.approved),
    Product(id=_uid("product:p12"), seller_id=SELLER2_ID, title="Watch Strap", description="Handstitched leather strap", price=Decimal("45.00"), currency="USD", image_url="https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=300", status=ProductStatus.approved),
    Product(id=_uid("product:p13"), seller_id=SELLER1_ID, title="Glazed Bowl", description="Glazed ceramic bowl", price=Decimal("22.00"), currency="USD", image_url="https://images.unsplash.com/photo-1578500492678-8b9b97e67149?w=300", status=ProductStatus.pending),
    Product(id=_uid("product:p14"), seller_id=SELLER1_ID, title="Raku Pot", description="Raku fired pot", price=Decimal("55.00"), currency="USD", image_url="https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=300", status=ProductStatus.pending),
    Product(id=_uid("product:p15"), seller_id=SELLER1_ID, title="Tea Set", description="4-piece tea set", price=Decimal("65.00"), currency="USD", image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=300", status=ProductStatus.pending),
    Product(id=_uid("product:p16"), seller_id=SELLER1_ID, title="Lamp Base", description="Ceramic lamp base", price=Decimal("42.00"), currency="USD", image_url="https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=300", status=ProductStatus.pending),
    Product(id=_uid("product:p17"), seller_id=SELLER1_ID, title="Butter Dish", description="Ceramic butter dish", price=Decimal("16.00"), currency="USD", image_url="https://images.unsplash.com/photo-1590794056226-79ef3aef7e6b?w=200", status=ProductStatus.pending),
    Product(id=_uid("product:p18"), seller_id=SELLER2_ID, title="Tote Bag", description="Leather tote bag", price=Decimal("89.00"), currency="USD", image_url="https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=300", status=ProductStatus.pending),
    Product(id=_uid("product:p19"), seller_id=SELLER2_ID, title="Leather Glasses Case", description="Protective glasses case", price=Decimal("28.00"), currency="USD", image_url="https://images.unsplash.com/photo-1544816155-12df9643f363?w=200", status=ProductStatus.pending),
    Product(id=_uid("product:p20"), seller_id=SELLER1_ID, title="Broken Bowl", description="Damaged bowl", price=Decimal("10.00"), currency="USD", image_url="https://images.unsplash.com/photo-1578500492678-8b9b97e67149?w=300", status=ProductStatus.rejected, rejection_reason="Item is damaged"),
    Product(id=_uid("product:p21"), seller_id=SELLER2_ID, title="Fake Leather", description="Not real leather", price=Decimal("25.00"), currency="USD", image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?w=300", status=ProductStatus.rejected, rejection_reason="Not genuine leather"),
    Product(id=_uid("product:p22"), seller_id=SELLER2_ID, title="Poor Quality", description="Low quality item", price=Decimal("20.00"), currency="USD", image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300", status=ProductStatus.rejected, rejection_reason="Poor craftsmanship"),
]

ORDERS = [
    Order(id=_uid("order:1"), customer_id=CUST1_ID, seller_id=SELLER1_ID, total=Decimal("44.49"), currency="USD", status=OrderStatus.pending, created_at=datetime.now(timezone.utc).replace(tzinfo=None), updated_at=datetime.now(timezone.utc).replace(tzinfo=None)),
    Order(id=_uid("order:2"), customer_id=CUST1_ID, seller_id=SELLER2_ID, total=Decimal("77.00"), currency="USD", status=OrderStatus.paid, created_at=datetime.now(timezone.utc).replace(tzinfo=None), updated_at=datetime.now(timezone.utc).replace(tzinfo=None)),
    Order(id=_uid("order:3"), customer_id=CUST2_ID, seller_id=SELLER1_ID, total=Decimal("29.99"), currency="USD", status=OrderStatus.accepted, created_at=datetime.now(timezone.utc).replace(tzinfo=None), updated_at=datetime.now(timezone.utc).replace(tzinfo=None)),
    Order(id=_uid("order:4"), customer_id=CUST2_ID, seller_id=SELLER2_ID, total=Decimal("59.00"), currency="USD", status=OrderStatus.out_for_delivery, created_at=datetime.now(timezone.utc).replace(tzinfo=None), updated_at=datetime.now(timezone.utc).replace(tzinfo=None)),
    Order(id=_uid("order:5"), customer_id=CUST1_ID, seller_id=SELLER1_ID, total=Decimal("14.50"), currency="USD", status=OrderStatus.delivered, created_at=datetime.now(timezone.utc).replace(tzinfo=None), updated_at=datetime.now(timezone.utc).replace(tzinfo=None)),
]

OIS = [
    OrderItem(id=_uid("oi:1"), order_id=ORDERS[0].id, product_id=PRODUCTS[0].id, title="Ceramic Vase", price=Decimal("29.99"), quantity=1, image_url=PRODUCTS[0].image_url),
    OrderItem(id=_uid("oi:2"), order_id=ORDERS[0].id, product_id=PRODUCTS[1].id, title="Clay Mug", price=Decimal("14.50"), quantity=1, image_url=PRODUCTS[1].image_url),
    OrderItem(id=_uid("oi:3"), order_id=ORDERS[1].id, product_id=PRODUCTS[6].id, title="Leather Wallet", price=Decimal("59.00"), quantity=1, image_url=PRODUCTS[6].image_url),
    OrderItem(id=_uid("oi:4"), order_id=ORDERS[1].id, product_id=PRODUCTS[7].id, title="Leather Belt", price=Decimal("18.00"), quantity=1, image_url=PRODUCTS[7].image_url),
    OrderItem(id=_uid("oi:5"), order_id=ORDERS[2].id, product_id=PRODUCTS[0].id, title="Ceramic Vase", price=Decimal("29.99"), quantity=1, image_url=PRODUCTS[0].image_url),
    OrderItem(id=_uid("oi:6"), order_id=ORDERS[3].id, product_id=PRODUCTS[6].id, title="Leather Wallet", price=Decimal("59.00"), quantity=1, image_url=PRODUCTS[6].image_url),
    OrderItem(id=_uid("oi:7"), order_id=ORDERS[4].id, product_id=PRODUCTS[1].id, title="Clay Mug", price=Decimal("14.50"), quantity=1, image_url=PRODUCTS[1].image_url),
]


async def seed() -> None:
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        for user in USERS:
            await session.execute(User.__table__.delete().where(User.id == user.id))
        for seller in SELLERS:
            await session.execute(Seller.__table__.delete().where(Seller.id == seller.id))
        for product in PRODUCTS:
            await session.execute(Product.__table__.delete().where(Product.id == product.id))
        for order in ORDERS:
            await session.execute(Order.__table__.delete().where(Order.id == order.id))
        for oi in OIS:
            await session.execute(OrderItem.__table__.delete().where(OrderItem.id == oi.id))
        for user in USERS:
            stmt = pg_insert(User).values(user.model_dump())
            await session.execute(stmt)
        for seller in SELLERS:
            stmt = pg_insert(Seller).values(seller.model_dump())
            await session.execute(stmt)
        for product in PRODUCTS:
            stmt = pg_insert(Product).values(product.model_dump())
            await session.execute(stmt)
        for order in ORDERS:
            stmt = pg_insert(Order).values(order.model_dump())
            await session.execute(stmt)
        for oi in OIS:
            stmt = pg_insert(OrderItem).values(oi.model_dump())
            await session.execute(stmt)
        await session.commit()
