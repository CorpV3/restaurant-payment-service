"""
triPOS Cloud client — sends sale transactions to a physical card terminal.

Worldpay triPOS Cloud API:
  Host: triposcert.vantiv.com (cert) / tripos.worldpay.com (prod)
  Endpoint: POST /api/v1/sale

Authentication: HMAC-SHA256 signature in tp-authorization header.
  HashKey = base64(HMAC-SHA256(requestBodyString, accountToken))
"""
import hashlib
import hmac
import base64
import json
import uuid
import httpx

from app.core.config import settings


def _build_auth_header(body: str) -> str:
    """Build tp-authorization header value with HMAC-SHA256 signature."""
    key = settings.TRIPOS_ACCOUNT_TOKEN.encode("utf-8")
    msg = body.encode("utf-8")
    hash_bytes = hmac.new(key, msg, hashlib.sha256).digest()
    hash_key = base64.b64encode(hash_bytes).decode("utf-8")
    return (
        f"Version=1.0,"
        f"AcceptorID={settings.TRIPOS_ACCEPTOR_ID},"
        f"ApplicationID={settings.TRIPOS_APPLICATION_ID},"
        f"ApplicationVersion=1.0.0,"
        f"ApplicationName=RestaurantPOS,"
        f"HashKey={hash_key}"
    )


async def charge_card_terminal(
    amount: float,
    order_ref: str,
    lane_id: int | None = None,
) -> dict:
    """
    Send a sale to the physical card terminal via triPOS Cloud.

    Blocks until customer taps/inserts card (up to 90 seconds).
    Returns the raw triPOS response dict.
    """
    lane = lane_id if lane_id is not None else settings.TRIPOS_LANE_ID

    payload = {
        "laneId": lane,
        "transactionAmount": round(amount, 2),
        "marketCode": "Retail",
        "referenceNumber": order_ref[:12],
        "clerkNumber": "1",
        "ticketNumber": order_ref[:20],
    }
    body = json.dumps(payload, separators=(",", ":"))
    request_id = str(uuid.uuid4())

    headers = {
        "Content-Type": "application/json",
        "tp-application-id": settings.TRIPOS_APPLICATION_ID,
        "tp-application-name": "RestaurantPOS",
        "tp-application-version": "1.0.0",
        "tp-authorization": _build_auth_header(body),
        "tp-express-acceptor-id": settings.TRIPOS_ACCEPTOR_ID,
        "tp-express-account-id": settings.TRIPOS_ACCOUNT_ID,
        "tp-express-account-token": settings.TRIPOS_ACCOUNT_TOKEN,
        "tp-request-id": request_id,
    }

    url = f"{settings.TRIPOS_BASE_URL}/api/v1/sale"
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, headers=headers, content=body)
        response.raise_for_status()
        return response.json()
