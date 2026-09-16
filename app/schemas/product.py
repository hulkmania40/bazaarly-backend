from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from app.models.product import ProductStatus


class ProductRead(BaseModel):
    id: str
    seller_id: str
    title: str
    description: str
    price: float
    currency: str
    image_url: str
    status: str
    rejection_reason: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: str
    updated_at: str


class ProductCreate(BaseModel):
    title: str
    description: str
    price: Decimal = Field(gt=0)
    currency: str = "USD"
    image_url: str


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    currency: Optional[str] = None
    image_url: Optional[str] = None


class RejectProduct(BaseModel):
    reason: str
