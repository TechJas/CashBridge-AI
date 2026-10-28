"""Cash-flow orchestration."""

from datetime import UTC, date, datetime
from uuid import UUID

from starlette.concurrency import run_in_threadpool

from app.db.repositories.businesses import BusinessRepository
from app.db.repositories.expenses import ExpenseRepository
from app.db.repositories.invoices import InvoiceRepository
from app.schemas.cash_flow import CashFlowSummary
from app.services.cash_flow import calculate_cash_flow


class BusinessNotFoundError(Exception):
    """The requested business does not exist."""


class CashFlowService:
    """Load a business snapshot and calculate its cash-flow summary."""

    def __init__(
        self,
        businesses: BusinessRepository,
        invoices: InvoiceRepository,
        expenses: ExpenseRepository,
    ) -> None:
        self._businesses = businesses
        self._invoices = invoices
        self._expenses = expenses

    async def summarize(
        self, business_id: UUID, as_of: date | None = None
    ) -> CashFlowSummary:
        """Return the deterministic cash-flow summary for a business."""
        business = await run_in_threadpool(self._businesses.get, business_id)
        if business is None:
            raise BusinessNotFoundError("Business not found.")

        invoices = await run_in_threadpool(
            self._invoices.list_for_business, business_id
        )
        expenses = await run_in_threadpool(
            self._expenses.list_for_business, business_id
        )

        return calculate_cash_flow(
            business=business,
            invoices=invoices,
            expenses=expenses,
            as_of=as_of or _utc_today(),
        )


def _utc_today() -> date:
    return datetime.now(UTC).date()
