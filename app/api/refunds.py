from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid

router = APIRouter()


class RefundStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None  # None means full refund
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    id: str
    payment_id: str
    amount: float
    currency: str
    status: RefundStatus
    reason: Optional[str]
    created_at: datetime


@router.post("/", response_model=RefundResponse)
async def create_refund(refund: RefundRequest):
    """Process a refund for a payment"""
    refund_id = str(uuid.uuid4())

    # TODO: Fetch original payment and process refund through gateway

    return RefundResponse(
        id=refund_id,
        payment_id=refund.payment_id,
        amount=refund.amount or 0,
        currency="GBP",
        status=RefundStatus.COMPLETED,
        reason=refund.reason,
        created_at=datetime.utcnow()
    )


@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(refund_id: str):
    """Get refund details"""
    raise HTTPException(status_code=404, detail="Refund not found")


@router.get("/payment/{payment_id}")
async def get_refunds_by_payment(payment_id: str):
    """Get all refunds for a payment"""
    return []
