from fastapi import APIRouter, Depends
from sqlmodel import select
from app.db.session import get_session
from app.core.deps import require_role
from app.models.order import Order
from app.models.seller import Seller
from app.schemas.order import OrderRead
from app.schemas.seller import SellerRead
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/admin/stats")
async def admin_stats(session: AsyncSession = Depends(get_session), _=Depends(require_role("admin"))):
    result = await session.execute(select(Order))
    orders = result.scalars().all()
    return {
        "pending_products": 0,
        "total_sellers": 0,
        "total_orders": len(orders),
        "revenue": 0.0,
    }


@router.get("/admin/sellers")
async def admin_sellers(session: AsyncSession = Depends(get_session), _=Depends(require_role("admin"))):
    result = await session.execute(select(Seller))
    sellers = result.scalars().all()
    return [SellerRead.model_validate(s) for s in sellers]


@router.get("/admin/orders", response_model=list[OrderRead])
async def admin_orders(status: str | None = None, session: AsyncSession = Depends(get_session), _=Depends(require_role("admin"))):
    stmt = select(Order)
    if status:
        stmt = stmt.where(Order.status == status)
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return [OrderRead.model_validate(o) for o in orders]
