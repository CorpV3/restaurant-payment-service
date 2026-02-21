from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import payments, gateways, refunds, health
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Payment Service starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    # Shutdown
    logger.info("Payment Service shutting down...")


app = FastAPI(
    title="Restaurant Payment Service",
    description="Payment processing service with UK gateway integrations (Stripe, SumUp)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(gateways.router, prefix="/api/v1/gateways", tags=["Gateways"])
app.include_router(refunds.router, prefix="/api/v1/refunds", tags=["Refunds"])


@app.get("/")
async def root():
    return {
        "service": "Restaurant Payment Service",
        "version": "1.0.0",
        "status": "running"
    }
