from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class Seller(SQLModel, table=True):
    __tablename__ = "sellers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, unique=True)
    store_name: str
    description: str = Field(sa_column_kwargs={"type_": "text"})
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="seller")
    products: list["Product"] = Relationship(back_populates="seller")
    orders: list["Order"] = Relationship(back_populates="seller")
