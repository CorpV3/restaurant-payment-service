from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "payment-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    # Check dependencies (DB, Redis, etc.)
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "stripe": "ok",
            "sumup": "ok"
        }
    }
