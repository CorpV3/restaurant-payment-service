from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import uuid

router = APIRouter()


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    GIFT_CARD = "gift_card"
    VOUCHER = "voucher"


class PaymentGateway(str, Enum):
    STRIPE = "stripe"
    SUMUP = "sumup"
    ZETTLE = "zettle"
    SQUARE = "square"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    currency: str = "GBP"
    method: PaymentMethod
    gateway: Optional[PaymentGateway] = None
    tip_amount: float = 0
    metadata: Optional[dict] = None


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    amount: float
    currency: str
    method: PaymentMethod
    gateway: Optional[PaymentGateway]
    status: PaymentStatus
    transaction_id: Optional[str]
    card_last_four: Optional[str]
    card_brand: Optional[str]
    receipt_url: Optional[str]
    created_at: datetime


@router.post("/process", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """Process a payment through the specified gateway"""
    payment_id = str(uuid.uuid4())

    # For cash payments, complete immediately
    if payment.method == PaymentMethod.CASH:
        return PaymentResponse(
            id=payment_id,
            order_id=payment.order_id,
            amount=payment.amount + payment.tip_amount,
            currency=payment.currency,
            method=payment.method,
            gateway=None,
            status=PaymentStatus.COMPLETED,
            transaction_id=f"CASH-{payment_id[:8]}",
            card_last_four=None,
            card_brand=None,
            receipt_url=None,
            created_at=datetime.utcnow()
        )

    # For card payments, process through gateway
    if payment.method == PaymentMethod.CARD:
        if not payment.gateway:
            payment.gateway = PaymentGateway.STRIPE  # Default gateway

        # Process through appropriate gateway
        if payment.gateway == PaymentGateway.STRIPE:
            return await process_stripe_payment(payment_id, payment)
        elif payment.gateway == PaymentGateway.SUMUP:
            return await process_sumup_payment(payment_id, payment)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported gateway: {payment.gateway}")

    raise HTTPException(status_code=400, detail=f"Unsupported payment method: {payment.method}")


async def process_stripe_payment(payment_id: str, payment: PaymentRequest) -> PaymentResponse:
    """Process payment through Stripe Terminal"""
    # TODO: Implement actual Stripe Terminal integration
    # For now, return a mock successful response
    return PaymentResponse(
        id=payment_id,
        order_id=payment.order_id,
        amount=payment.amount + payment.tip_amount,
        currency=payment.currency,
        method=payment.method,
        gateway=PaymentGateway.STRIPE,
        status=PaymentStatus.COMPLETED,
        transaction_id=f"pi_{payment_id[:16]}",
        card_last_four="4242",
        card_brand="visa",
        receipt_url=f"https://pay.stripe.com/receipts/{payment_id}",
        created_at=datetime.utcnow()
    )


async def process_sumup_payment(payment_id: str, payment: PaymentRequest) -> PaymentResponse:
    """Process payment through SumUp"""
    # TODO: Implement actual SumUp integration
    return PaymentResponse(
        id=payment_id,
        order_id=payment.order_id,
        amount=payment.amount + payment.tip_amount,
        currency=payment.currency,
        method=payment.method,
        gateway=PaymentGateway.SUMUP,
        status=PaymentStatus.COMPLETED,
        transaction_id=f"SU-{payment_id[:12]}",
        card_last_four="1234",
        card_brand="mastercard",
        receipt_url=None,
        created_at=datetime.utcnow()
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get payment details by ID"""
    # TODO: Fetch from database
    raise HTTPException(status_code=404, detail="Payment not found")


@router.get("/order/{order_id}")
async def get_payments_by_order(order_id: str):
    """Get all payments for an order"""
    # TODO: Fetch from database
    return []


@router.post("/{payment_id}/capture")
async def capture_payment(payment_id: str):
    """Capture a pre-authorized payment"""
    # TODO: Implement capture logic
    return {"status": "captured", "payment_id": payment_id}
