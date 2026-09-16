import stripe
from app.core.config import settings

stripe.api_key = settings.stripe_secret_key


class PaymentService:
    @staticmethod
    async def create_intent(order_ids: list[str]) -> dict:
        intent = stripe.PaymentIntent.create(
            amount=1000,
            currency="usd",
            metadata={"order_ids": ",".join(order_ids)},
        )
        return {"client_secret": intent.client_secret, "payment_intent_id": intent.id}

    @staticmethod
    async def handle_webhook(payload: bytes, sig_header: str) -> dict:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            return {"payment_intent_id": intent["id"], "status": "succeeded"}
        return {"status": "ignored"}
