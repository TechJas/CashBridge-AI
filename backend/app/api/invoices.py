"""Invoice routes backed by the PayPal Sandbox."""

from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.integrations.paypal import (
    PayPalAuthenticationError,
    PayPalClient,
    PayPalConnectionError,
    PayPalError,
    PayPalResponseError,
    PayPalTimeoutError,
)
from app.schemas.invoice import InvoiceListResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number, starting at 1.",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of invoices per page (1-100).",
    ),
) -> InvoiceListResponse:
    """Return invoice history from the PayPal Sandbox."""
    settings = get_settings()
    if not settings.paypal_is_configured:
        raise HTTPException(
            status_code=503,
            detail="PayPal credentials are not configured.",
        )

    service = InvoiceService(
        PayPalClient(
            client_id=settings.paypal_client_id,
            client_secret=settings.paypal_client_secret,
        )
    )

    try:
        return await service.list_invoices(page=page, page_size=page_size)
    except PayPalTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="PayPal request timed out.",
        ) from exc
    except PayPalAuthenticationError as exc:
        raise HTTPException(
            status_code=502,
            detail="PayPal authentication failed.",
        ) from exc
    except PayPalConnectionError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to PayPal.",
        ) from exc
    except PayPalResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail="PayPal returned an unexpected response.",
        ) from exc
    except PayPalError as exc:
        raise HTTPException(
            status_code=502,
            detail="PayPal request failed.",
        ) from exc
