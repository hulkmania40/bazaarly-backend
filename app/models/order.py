from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    accepted = "accepted"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="users.id", index=True)
    seller_id: UUID = Field(foreign_key="sellers.id", index=True)
    total: Decimal = Field(sa_column_kwargs={"type_": "NUMERIC(10,2)"})
    currency: str = "USD"
    status: OrderStatus = Field(default=OrderStatus.pending, index=True)
    payment_ref: Optional[str] = Field(default=None, index=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    customer: "User" = Relationship(back_populates="orders_as_customer")
    seller: "Seller" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="orders.id", index=True)
    product_id: UUID = Field(foreign_key="products.id")
    title: str
    price: Decimal = Field(sa_column_kwargs={"type_": "NUMERIC(10,2)"})
    quantity: int
    image_url: str

    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")
