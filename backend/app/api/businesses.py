"""Local-only business routes."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_business_service, require_local_access
from app.db.errors import RepositoryError
from app.schemas.cash_flow import BusinessSummary
from app.services.business_service import BusinessService

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"],
    dependencies=[Depends(require_local_access)],
)


@router.get("", response_model=list[BusinessSummary])
async def list_businesses(
    service: BusinessService = Depends(get_business_service),
) -> list[BusinessSummary]:
    """Return businesses available in the local demo database."""
    try:
        return await service.list_businesses()
    except RepositoryError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load businesses.",
        ) from exc
