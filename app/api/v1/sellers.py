from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.db.session import get_session
from app.core.deps import get_current_user, require_role
from app.models.seller import Seller
from app.models.product import Product, ProductStatus
from app.schemas.seller import SellerRead, SellerUpdate
from app.schemas.product import ProductRead
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/sellers")
async def list_sellers(session: AsyncSession = Depends(get_session), _=Depends(require_role("customer", "admin"))):
    result = await session.execute(select(Seller))
    sellers = result.scalars().all()
    return [SellerRead.model_validate(s) for s in sellers]


@router.get("/sellers/me", response_model=SellerRead)
async def my_seller(session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    result = await session.execute(select(Seller).where(Seller.user_id == current_user.id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    return SellerRead.model_validate(seller)


@router.patch("/sellers/me", response_model=SellerRead)
async def update_my_seller(data: SellerUpdate, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    result = await session.execute(select(Seller).where(Seller.user_id == current_user.id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(seller, k, v)
    await session.commit()
    await session.refresh(seller)
    return SellerRead.model_validate(seller)


@router.get("/sellers/{seller_id}", response_model=SellerRead)
async def get_seller(seller_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    return SellerRead.model_validate(seller)


@router.get("/sellers/{seller_id}/products", response_model=list[ProductRead])
async def seller_products(seller_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("customer", "admin"))):
    result = await session.execute(select(Product).where(Product.seller_id == seller_id, Product.status == ProductStatus.approved))
    products = result.scalars().all()
    return [ProductRead.model_validate(p) for p in products]
