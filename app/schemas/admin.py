from pydantic import BaseModel


class AdminStats(BaseModel):
    pending_products: int
    total_sellers: int
    total_orders: int
    revenue: float
