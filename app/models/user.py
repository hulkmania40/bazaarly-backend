from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class Role(str, Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: Role = Field(sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})

    seller: Optional["Seller"] = Relationship(back_populates="user")
    products_approved: list["Product"] = Relationship(back_populates="approved_by_user")
    orders_as_customer: list["Order"] = Relationship(back_populates="customer")
    orders_as_seller: list["Order"] = Relationship(back_populates="seller")
