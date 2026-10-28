"""CashBridge AI FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.invoices import router as invoices_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="CashBridge AI API",
    description="Backend API for the CashBridge AI cash-flow assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoices_router, prefix="/api")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok", "service": "cashbridge-api"}
