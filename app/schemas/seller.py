from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserRead


class SellerRead(BaseModel):
    id: str
    user_id: str
    store_name: str
    description: str
    avatar_url: Optional[str] = None
    product_count: Optional[int] = None
    created_at: str


class SellerWithUser(SellerRead):
    user: Optional[UserRead] = None


class SellerUpdate(BaseModel):
    store_name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
