"""Local-only cash-flow routes."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_cash_flow_service, require_local_access
from app.db.errors import RepositoryError
from app.schemas.cash_flow import CashFlowSummary
from app.services.cash_flow import CurrencyMismatchError
from app.services.cash_flow_service import (
    BusinessNotFoundError,
    CashFlowService,
)

router = APIRouter(
    prefix="/cash-flow",
    tags=["cash-flow"],
    dependencies=[Depends(require_local_access)],
)


@router.get("/summary", response_model=CashFlowSummary)
async def get_cash_flow_summary(
    business_id: UUID,
    as_of: date | None = Query(
        default=None,
        description="Calculation date in ISO form. Defaults to today in UTC.",
    ),
    service: CashFlowService = Depends(get_cash_flow_service),
) -> CashFlowSummary:
    """Return a deterministic cash-flow summary for one business."""
    try:
        return await service.summarize(business_id, as_of=as_of)
    except BusinessNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Business not found.",
        ) from exc
    except CurrencyMismatchError as exc:
        raise HTTPException(
            status_code=409,
            detail="Records do not use the business base currency.",
        ) from exc
    except RepositoryError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load financial data.",
        ) from exc
