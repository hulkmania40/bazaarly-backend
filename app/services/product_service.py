from sqlmodel import select
from app.models.product import Product, ProductStatus
from app.schemas.product import ProductCreate, ProductUpdate
from datetime import datetime, timezone


class ProductService:
    @staticmethod
    async def list_products(session, status: str | None = None, seller_id: str | None = None, page: int = 1, page_size: int = 20) -> list[Product]:
        stmt = select(Product)
        if status:
            stmt = stmt.where(Product.status == ProductStatus(status))
        if seller_id:
            stmt = stmt.where(Product.seller_id == seller_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(session, seller_id: str, data: ProductCreate) -> Product:
        product = Product(seller_id=seller_id, **data.model_dump())
        session.add(product)
        await session.flush()
        await session.refresh(product)
        return product

    @staticmethod
    async def update(session, product_id: str, data: ProductUpdate) -> Product:
        product = await session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(product, k, v)
        product.status = ProductStatus.pending
        product.updated_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(product)
        return product

    @staticmethod
    async def delete(session, product_id: str) -> None:
        product = await session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        if product.status not in (ProductStatus.pending, ProductStatus.rejected):
            raise ValueError("Cannot delete product in current status")
        await session.delete(product)
        await session.flush()

    @staticmethod
    async def approve(session, product_id: str, approved_by: str) -> Product:
        product = await session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        product.status = ProductStatus.approved
        product.approved_by = approved_by
        product.approved_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(product)
        return product

    @staticmethod
    async def reject(session, product_id: str, reason: str) -> Product:
        product = await session.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        product.status = ProductStatus.rejected
        product.rejection_reason = reason
        await session.flush()
        await session.refresh(product)
        return product
