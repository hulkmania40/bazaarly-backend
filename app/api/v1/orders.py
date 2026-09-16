from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.db.session import get_session
from app.core.deps import get_current_user, require_role
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderRead, CheckoutRequest, ConfirmOrderRequest
from app.services.order_service import OrderService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/orders/checkout", status_code=201)
async def checkout(data: CheckoutRequest, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("customer"))):
    orders = await OrderService.checkout(session, str(current_user.id), [i.model_dump() for i in data.items], data.payment_method)
    await session.commit()
    return {"orders": [OrderRead.model_validate(o) for o in orders], "payment_intent": {"client_secret": "stub_client_secret"}}


@router.post("/orders/confirm", response_model=list[OrderRead])
async def confirm(data: ConfirmOrderRequest, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("customer"))):
    orders = await OrderService.confirm(session, data.payment_ref, data.order_ids)
    await session.commit()
    return [OrderRead.model_validate(o) for o in orders]


@router.get("/orders/mine", response_model=list[OrderRead])
async def my_orders(session: AsyncSession = Depends(get_session), current_user=Depends(require_role("customer"))):
    result = await session.execute(select(Order).where(Order.customer_id == current_user.id))
    orders = result.scalars().all()
    return [OrderRead.model_validate(o) for o in orders]


@router.get("/orders/seller/mine", response_model=list[OrderRead])
async def seller_orders(session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    result = await session.execute(select(Order).where(Order.seller_id == current_user.id))
    orders = result.scalars().all()
    return [OrderRead.model_validate(o) for o in orders]


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    return OrderRead.model_validate(order)


@router.post("/orders/{order_id}/accept", response_model=OrderRead)
async def accept_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order = await OrderService.advance_status(session, order_id, str(current_user.id), current_user.role, OrderStatus.accepted.value)
    await session.commit()
    return OrderRead.model_validate(order)


@router.post("/orders/{order_id}/ship", response_model=OrderRead)
async def ship_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order = await OrderService.advance_status(session, order_id, str(current_user.id), current_user.role, OrderStatus.out_for_delivery.value)
    await session.commit()
    return OrderRead.model_validate(order)


@router.post("/orders/{order_id}/deliver", response_model=OrderRead)
async def deliver_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order = await OrderService.advance_status(session, order_id, str(current_user.id), current_user.role, OrderStatus.delivered.value)
    await session.commit()
    return OrderRead.model_validate(order)


@router.post("/orders/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(order_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    order = await OrderService.advance_status(session, order_id, str(current_user.id), current_user.role, OrderStatus.cancelled.value)
    await session.commit()
    return OrderRead.model_validate(order)
