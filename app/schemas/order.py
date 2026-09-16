from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from app.models.order import OrderStatus


class OrderItemRead(BaseModel):
    id: str
    product_id: str
    title: str
    price: float
    quantity: int
    image_url: str


class OrderRead(BaseModel):
    id: str
    customer_id: str
    seller_id: str
    total: float
    currency: str
    status: str
    payment_ref: Optional[str] = None
    items: list[OrderItemRead] = []
    created_at: str
    updated_at: str


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
