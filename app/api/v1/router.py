from fastapi import APIRouter
from app.api.v1 import auth, users, sellers, products, orders, admin, payments, uploads

router = APIRouter()
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(sellers.router)
router.include_router(products.router)
router.include_router(orders.router)
router.include_router(admin.router)
router.include_router(payments.router)
router.include_router(uploads.router)
