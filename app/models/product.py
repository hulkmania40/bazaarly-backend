from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric, Text


class ProductStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    seller_id: UUID = Field(foreign_key="sellers.id", index=True)
    title: str
    description: str = Field(sa_column=Column("description", Text()))
    price: Decimal = Field(sa_column=Column("price", Numeric(10, 2)))
    currency: str = "USD"
    image_url: str
    status: ProductStatus = Field(default=ProductStatus.pending, index=True)
    rejection_reason: Optional[str] = Field(sa_column=Column("rejection_reason", Text()), default=None)
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    seller: "Seller" = Relationship(back_populates="products")
    approved_by_user: Optional["User"] = Relationship(back_populates="products_approved")
    order_items: list["OrderItem"] = Relationship(back_populates="product")
