from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.db.session import get_session
from app.core.deps import get_current_user, require_role
from app.models.product import Product, ProductStatus
from app.models.seller import Seller
from app.schemas.product import ProductRead, ProductCreate, ProductUpdate, RejectProduct
from app.services.product_service import ProductService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/products")
async def list_products(status: str | None = None, seller_id: str | None = None, page: int = 1, page_size: int = 20, session: AsyncSession = Depends(get_session), _=Depends(require_role("admin"))):
    products = await ProductService.list_products(session, status=status, seller_id=seller_id, page=page, page_size=page_size)
    return [ProductRead.model_validate(p) for p in products]


@router.get("/products/mine", response_model=list[ProductRead])
async def my_products(session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    result = await session.execute(select(Seller).where(Seller.user_id == current_user.id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    products = (await session.execute(select(Product).where(Product.seller_id == seller.id))).scalars().all()
    return [ProductRead.model_validate(p) for p in products]


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    if current_user.role == "customer" and product.status != ProductStatus.approved:
        raise HTTPException(status_code=403, detail="FORBIDDEN_ROLE")
    return ProductRead.model_validate(product)


@router.post("/products", status_code=201, response_model=ProductRead)
async def create_product(data: ProductCreate, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    result = await session.execute(select(Seller).where(Seller.user_id == current_user.id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    product = await ProductService.create(session, str(seller.id), data)
    return ProductRead.model_validate(product)


@router.patch("/products/{product_id}", response_model=ProductRead)
async def update_product(product_id: str, data: ProductUpdate, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    result = await session.execute(select(Seller).where(Seller.user_id == current_user.id))
    seller = result.scalar_one_or_none()
    if not seller or product.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN_ROLE")
    product = await ProductService.update(session, product_id, data)
    return ProductRead.model_validate(product)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: str, session: AsyncSession = Depends(get_session), current_user=Depends(require_role("seller"))):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    result = await session.execute(select(Seller).where(Seller.user_id == current_user.id))
    seller = result.scalar_one_or_none()
    if not seller or product.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN_ROLE")
    if product.status not in (ProductStatus.pending, ProductStatus.rejected):
        raise HTTPException(status_code=409, detail="INVALID_STATUS_TRANSITION")
    await session.delete(product)
    await session.commit()


@router.post("/products/{product_id}/approve", response_model=ProductRead)
async def approve_product(product_id: str, session: AsyncSession = Depends(get_session), _=Depends(require_role("admin"))):
    product = await ProductService.approve(session, product_id, "")
    return ProductRead.model_validate(product)


@router.post("/products/{product_id}/reject", response_model=ProductRead)
async def reject_product(product_id: str, data: RejectProduct, session: AsyncSession = Depends(get_session), _=Depends(require_role("admin"))):
    product = await ProductService.reject(session, product_id, data.reason)
    return ProductRead.model_validate(product)
