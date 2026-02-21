from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

router = APIRouter()


class GatewayStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONFIGURING = "configuring"


class GatewayInfo(BaseModel):
    id: str
    name: str
    display_name: str
    status: GatewayStatus
    enabled: bool
    supports_terminal: bool
    supports_online: bool
    transaction_fee_percent: float
    transaction_fee_fixed: float
    currency: str = "GBP"


class StripeConnectionToken(BaseModel):
    secret: str
    expires_at: int


@router.get("/", response_model=List[GatewayInfo])
async def list_gateways():
    """List all available payment gateways"""
    return [
        GatewayInfo(
            id="stripe",
            name="stripe",
            display_name="Stripe Terminal",
            status=GatewayStatus.ACTIVE,
            enabled=True,
            supports_terminal=True,
            supports_online=True,
            transaction_fee_percent=1.4,
            transaction_fee_fixed=0.20,
            currency="GBP"
        ),
        GatewayInfo(
            id="sumup",
            name="sumup",
            display_name="SumUp",
            status=GatewayStatus.ACTIVE,
            enabled=True,
            supports_terminal=True,
            supports_online=False,
            transaction_fee_percent=1.69,
            transaction_fee_fixed=0.0,
            currency="GBP"
        ),
        GatewayInfo(
            id="zettle",
            name="zettle",
            display_name="Zettle by PayPal",
            status=GatewayStatus.INACTIVE,
            enabled=False,
            supports_terminal=True,
            supports_online=False,
            transaction_fee_percent=1.75,
            transaction_fee_fixed=0.0,
            currency="GBP"
        ),
        GatewayInfo(
            id="square",
            name="square",
            display_name="Square",
            status=GatewayStatus.INACTIVE,
            enabled=False,
            supports_terminal=True,
            supports_online=True,
            transaction_fee_percent=1.75,
            transaction_fee_fixed=0.0,
            currency="GBP"
        ),
    ]


@router.get("/{gateway_id}", response_model=GatewayInfo)
async def get_gateway(gateway_id: str):
    """Get gateway details"""
    gateways = await list_gateways()
    for gateway in gateways:
        if gateway.id == gateway_id:
            return gateway
    raise HTTPException(status_code=404, detail="Gateway not found")


@router.post("/{gateway_id}/enable")
async def enable_gateway(gateway_id: str):
    """Enable a payment gateway"""
    return {"status": "enabled", "gateway_id": gateway_id}


@router.post("/{gateway_id}/disable")
async def disable_gateway(gateway_id: str):
    """Disable a payment gateway"""
    return {"status": "disabled", "gateway_id": gateway_id}


# Stripe Terminal specific endpoints
@router.post("/stripe/connection-token", response_model=StripeConnectionToken)
async def create_stripe_connection_token():
    """Create a Stripe Terminal connection token"""
    # TODO: Implement actual Stripe connection token creation
    # import stripe
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # connection_token = stripe.terminal.ConnectionToken.create()
    return StripeConnectionToken(
        secret="pst_test_mock_token_12345",
        expires_at=1800  # 30 minutes
    )


@router.post("/stripe/create-payment-intent")
async def create_stripe_payment_intent(amount: int, currency: str = "gbp"):
    """Create a Stripe PaymentIntent for terminal"""
    # TODO: Implement actual Stripe PaymentIntent creation
    return {
        "id": "pi_mock_12345",
        "client_secret": "pi_mock_12345_secret_67890",
        "amount": amount,
        "currency": currency
    }


# SumUp specific endpoints
@router.post("/sumup/checkout")
async def create_sumup_checkout(amount: float, currency: str = "GBP", description: str = ""):
    """Create a SumUp checkout"""
    # TODO: Implement actual SumUp checkout
    return {
        "id": "sumup_checkout_12345",
        "amount": amount,
        "currency": currency,
        "status": "pending"
    }


@router.get("/sumup/checkout/{checkout_id}")
async def get_sumup_checkout_status(checkout_id: str):
    """Get SumUp checkout status"""
    return {
        "id": checkout_id,
        "status": "completed",
        "transaction_id": "SUMUP-TXN-12345"
    }
