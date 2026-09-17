from pydantic import BaseModel, ConfigDict, BeforeValidator
from typing import Optional, Annotated
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.schemas.user import UserRead


def _coerce_str(v):
    if isinstance(v, (str, int, float, UUID, datetime, Decimal)):
        return str(v)
    return v


SellerId = Annotated[str, BeforeValidator(_coerce_str)]
SellerUserId = Annotated[str, BeforeValidator(_coerce_str)]
SellerCreatedAt = Annotated[str, BeforeValidator(_coerce_str)]


class SellerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: SellerId
    user_id: SellerUserId
    store_name: str
    description: str
    avatar_url: Optional[str] = None
    product_count: Optional[int] = None
    created_at: SellerCreatedAt


class SellerWithUser(SellerRead):
    user: Optional[UserRead] = None


class SellerUpdate(BaseModel):
    store_name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
