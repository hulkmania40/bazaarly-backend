from pydantic import BaseModel, ConfigDict, BeforeValidator, Field
from decimal import Decimal
from typing import Optional, Annotated
from uuid import UUID
from datetime import datetime
from app.models.order import OrderStatus


def _coerce_str(v):
    if isinstance(v, (str, int, float, UUID, datetime, Decimal)):
        return str(v)
    return v

def _coerce_float(v):
    if isinstance(v, (int, float, Decimal)):
        return float(v)
    return v


OrderId = Annotated[str, BeforeValidator(_coerce_str)]
OrderCustomerId = Annotated[str, BeforeValidator(_coerce_str)]
OrderSellerId = Annotated[str, BeforeValidator(_coerce_str)]
OrderTotal = Annotated[float, BeforeValidator(_coerce_float)]
OrderTimestamp = Annotated[str, BeforeValidator(_coerce_str)]
OiId = Annotated[str, BeforeValidator(_coerce_str)]
OiProductId = Annotated[str, BeforeValidator(_coerce_str)]
OiPrice = Annotated[float, BeforeValidator(_coerce_float)]


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: OiId
    product_id: OiProductId
    title: str
    price: OiPrice
    quantity: int
    image_url: str


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: OrderId
    customer_id: OrderCustomerId
    seller_id: OrderSellerId
    total: OrderTotal
    currency: str
    status: str
    payment_ref: Optional[str] = None
    items: list[OrderItemRead] = []
    created_at: OrderTimestamp
    updated_at: OrderTimestamp


class OrderCreateItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class CheckoutRequest(BaseModel):
    items: list[OrderCreateItem]
    payment_method: str


class ConfirmOrderRequest(BaseModel):
    payment_ref: str
    order_ids: list[str]


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
