from pydantic import BaseModel, ConfigDict, BeforeValidator, Field
from decimal import Decimal
from typing import Optional, Annotated
from uuid import UUID
from datetime import datetime


def _coerce_str(v):
    if isinstance(v, (str, int, float, UUID, datetime, Decimal)):
        return str(v)
    return v

def _coerce_float(v):
    if isinstance(v, (int, float, Decimal)):
        return float(v)
    return v


ProductId = Annotated[str, BeforeValidator(_coerce_str)]
ProductSellerId = Annotated[str, BeforeValidator(_coerce_str)]
ProductTimestamp = Annotated[str, BeforeValidator(_coerce_str)]
ProductPrice = Annotated[float, BeforeValidator(_coerce_float)]


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: ProductId
    seller_id: ProductSellerId
    title: str
    description: str
    price: ProductPrice
    currency: str
    image_url: str
    status: str
    rejection_reason: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: ProductTimestamp
    updated_at: ProductTimestamp


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
