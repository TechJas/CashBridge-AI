"""CashBridge AI FastAPI application."""

from fastapi import FastAPI

app = FastAPI(
    title="CashBridge AI API",
    description="Backend API for the CashBridge AI cash-flow assistant.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok", "service": "cashbridge-api"}
