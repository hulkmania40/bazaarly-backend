from sqlmodel import select
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product, ProductStatus
from app.core.errors import ValidationError, ConflictError
from decimal import Decimal
from uuid import UUID


class OrderService:
    @staticmethod
    async def checkout(session, customer_id: str, items_data: list[dict], payment_method: str) -> list[Order]:
        product_ids = [UUID(i["product_id"]) for i in items_data]
        products = {p.id: p for p in (await session.execute(select(Product).where(Product.id.in_(product_ids)))).scalars().all()}

        unavailable = [pid for pid, p in products.items() if p.status != ProductStatus.approved]
        if unavailable:
            raise ValidationError("PRODUCT_NOT_AVAILABLE", "One or more products are not available")

        by_seller: dict[str, list[dict]] = {}
        for item in items_data:
            by_seller.setdefault(str(products[UUID(item["product_id"])].seller_id), []).append(item)

        orders: list[Order] = []
        for seller_id, seller_items in by_seller.items():
            total = sum(Decimal(str(products[UUID(i["product_id"])].price)) * i["quantity"] for i in seller_items)
            order = Order(customer_id=UUID(customer_id), seller_id=UUID(seller_id), total=total, currency="USD", status=OrderStatus.pending)
            session.add(order)
            await session.flush()
            for item in seller_items:
                p = products[UUID(item["product_id"])]
                oi = OrderItem(order_id=order.id, product_id=p.id, title=p.title, price=p.price, quantity=item["quantity"], image_url=p.image_url)
                session.add(oi)
            orders.append(order)
        await session.flush()
        for o in orders:
            await session.refresh(o)
        return orders

    @staticmethod
    async def confirm(session, payment_ref: str, order_ids: list[str]) -> list[Order]:
        orders = (await session.execute(select(Order).where(Order.id.in_(order_ids)))).scalars().all()
        for order in orders:
            if order.status != OrderStatus.pending:
                raise ConflictError("INVALID_STATUS_TRANSITION", f"Order {order.id} is not in pending status")
            order.status = OrderStatus.paid
            order.payment_ref = payment_ref
            await session.flush()
            await session.refresh(order)
        return orders

    @staticmethod
    async def advance_status(session, order_id: str, user_id: str, role: str, target_status: str) -> Order:
        order = await session.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")

        valid_transitions = {
            OrderStatus.pending: [OrderStatus.paid, OrderStatus.cancelled],
            OrderStatus.paid: [OrderStatus.accepted, OrderStatus.cancelled],
            OrderStatus.accepted: [OrderStatus.out_for_delivery, OrderStatus.cancelled],
            OrderStatus.out_for_delivery: [OrderStatus.delivered, OrderStatus.cancelled],
            OrderStatus.delivered: [],
            OrderStatus.cancelled: [],
        }
        target = OrderStatus(target_status)
        if target not in valid_transitions[order.status]:
            raise ConflictError("INVALID_STATUS_TRANSITION", f"Cannot transition from {order.status} to {target_status}")

        if role == "seller" and order.seller_id != UUID(user_id):
            raise ValueError("Not your order")

        order.status = target
        await session.flush()
        await session.refresh(order)
        return order
