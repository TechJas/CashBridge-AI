"""Business listing orchestration."""

from starlette.concurrency import run_in_threadpool

from app.db.repositories.businesses import BusinessRepository
from app.schemas.cash_flow import BusinessSummary


class BusinessService:
    """List businesses available to the local development client."""

    def __init__(self, businesses: BusinessRepository) -> None:
        self._businesses = businesses

    async def list_businesses(self) -> list[BusinessSummary]:
        """Return all businesses ordered by name."""
        records = await run_in_threadpool(self._businesses.list_all)
        return [
            BusinessSummary(
                id=record.id,
                name=record.name,
                base_currency=record.base_currency,
            )
            for record in records
        ]
