"""Cash-flow service orchestration tests."""

from datetime import date
from uuid import UUID

import pytest
from app.db.models import BusinessRecord, ExpenseRecord, InvoiceRecord
from app.services.cash_flow_service import (
    BusinessNotFoundError,
    CashFlowService,
)

BUSINESS = BusinessRecord(
    id=UUID("11111111-1111-4111-8111-111111111111"),
    name="Bridgewater Design Studio",
    base_currency="USD",
)
AS_OF = date(2026, 10, 28)


class FakeBusinessRepository:
    def __init__(self, record: BusinessRecord | None) -> None:
        self._record = record

    def get(self, business_id: UUID) -> BusinessRecord | None:
        return self._record


class FakeInvoiceRepository:
    def list_for_business(self, business_id: UUID) -> list[InvoiceRecord]:
        return [
            InvoiceRecord(
                id=UUID(int=1),
                status="SENT",
                due_date=date(2026, 11, 1),
                currency_code="USD",
                total_minor_units=50000,
                amount_due_minor_units=50000,
            )
        ]


class FakeExpenseRepository:
    def list_for_business(self, business_id: UUID) -> list[ExpenseRecord]:
        return [
            ExpenseRecord(
                id=UUID(int=2),
                status="planned",
                due_date=date(2026, 11, 2),
                currency_code="USD",
                amount_minor_units=12000,
            )
        ]


async def test_service_uses_explicit_as_of_date() -> None:
    service = CashFlowService(
        FakeBusinessRepository(BUSINESS),
        FakeInvoiceRepository(),
        FakeExpenseRepository(),
    )

    summary = await service.summarize(BUSINESS.id, as_of=AS_OF)

    assert summary.as_of == AS_OF
    assert summary.business_id == BUSINESS.id
    assert summary.outstanding_receivables_minor_units == 50000
    assert summary.planned_expenses_minor_units == 12000
    assert summary.horizons[0].net_cash_flow_minor_units == 38000


async def test_missing_business_raises() -> None:
    service = CashFlowService(
        FakeBusinessRepository(None),
        FakeInvoiceRepository(),
        FakeExpenseRepository(),
    )

    with pytest.raises(BusinessNotFoundError):
        await service.summarize(BUSINESS.id, as_of=AS_OF)
