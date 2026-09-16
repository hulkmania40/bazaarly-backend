from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.deps import require_role
from app.services.payment_service import PaymentService
from app.schemas.order import PaymentIntentResponse

router = APIRouter()


@router.post("/payments/create-intent", response_model=PaymentIntentResponse)
async def create_intent(body: dict, _=Depends(require_role("customer"))):
    order_ids = body.get("order_ids", [])
    result = await PaymentService.create_intent(order_ids)
    return PaymentIntentResponse(client_secret=result["client_secret"], payment_intent_id=result["payment_intent_id"])


@router.post("/payments/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    result = await PaymentService.handle_webhook(payload, sig_header)
    return result
