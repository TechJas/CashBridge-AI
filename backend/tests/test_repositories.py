"""Repository query and mapping tests with a fake Supabase client."""

from datetime import date
from typing import Any
from uuid import UUID

import pytest
from app.db.errors import RepositoryError
from app.db.repositories.businesses import BusinessRepository
from app.db.repositories.expenses import ExpenseRepository
from app.db.repositories.invoices import InvoiceRepository

BUSINESS_ID = UUID("11111111-1111-4111-8111-111111111111")
OTHER_BUSINESS_ID = UUID("99999999-9999-4999-8999-999999999999")


class FakeResponse:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data


class FakeQuery:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows
        self._filters: dict[str, Any] = {}
        self._limit: int | None = None
        self.selected_columns: str | None = None

    def select(self, columns: str) -> "FakeQuery":
        self.selected_columns = columns
        return self

    def eq(self, column: str, value: Any) -> "FakeQuery":
        self._filters[column] = value
        return self

    def order(self, column: str, desc: bool = False) -> "FakeQuery":
        return self

    def limit(self, value: int) -> "FakeQuery":
        self._limit = value
        return self

    def execute(self) -> FakeResponse:
        rows = [
            row
            for row in self._rows
            if all(row.get(key) == value for key, value in self._filters.items())
        ]
        if self._limit is not None:
            rows = rows[: self._limit]
        return FakeResponse(rows)


class FakeTable:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def select(self, columns: str) -> FakeQuery:
        return FakeQuery(self._rows).select(columns)


class FakeClient:
    def __init__(self, tables: dict[str, list[dict[str, Any]]]) -> None:
        self._tables = tables

    def table(self, name: str) -> FakeTable:
        return FakeTable(self._tables[name])


def _business_row(business_id: UUID = BUSINESS_ID) -> dict[str, Any]:
    return {
        "id": str(business_id),
        "name": "Bridgewater Design Studio",
        "base_currency": "USD",
    }


def _invoice_row(business_id: UUID = BUSINESS_ID) -> dict[str, Any]:
    return {
        "id": "33333333-3333-4333-8333-333333333301",
        "status": "SENT",
        "due_date": "2026-11-05",
        "currency_code": "USD",
        "total_minor_units": 480000,
        "amount_due_minor_units": 480000,
        "business_id": str(business_id),
    }


def _expense_row(business_id: UUID = BUSINESS_ID) -> dict[str, Any]:
    return {
        "id": "44444444-4444-4444-8444-444444444401",
        "status": "planned",
        "due_date": "2026-11-01",
        "currency_code": "USD",
        "amount_minor_units": 350000,
        "business_id": str(business_id),
    }


def test_business_repository_maps_rows() -> None:
    repository = BusinessRepository(
        FakeClient({"businesses": [_business_row(), _business_row(OTHER_BUSINESS_ID)]})
    )

    records = repository.list_all()

    assert len(records) == 2
    assert records[0].name == "Bridgewater Design Studio"
    assert records[0].base_currency == "USD"


def test_business_repository_filters_by_id() -> None:
    repository = BusinessRepository(
        FakeClient({"businesses": [_business_row(), _business_row(OTHER_BUSINESS_ID)]})
    )

    record = repository.get(BUSINESS_ID)

    assert record is not None
    assert record.id == BUSINESS_ID


def test_business_repository_returns_none_when_missing() -> None:
    repository = BusinessRepository(FakeClient({"businesses": []}))

    assert repository.get(BUSINESS_ID) is None


def test_invoice_repository_filters_by_business() -> None:
    repository = InvoiceRepository(
        FakeClient(
            {
                "invoices": [
                    _invoice_row(),
                    _invoice_row(OTHER_BUSINESS_ID),
                ]
            }
        )
    )

    records = repository.list_for_business(BUSINESS_ID)

    assert len(records) == 1
    assert records[0].status == "SENT"
    assert records[0].due_date == date(2026, 11, 5)
    assert records[0].amount_due_minor_units == 480000


def test_expense_repository_maps_rows() -> None:
    repository = ExpenseRepository(FakeClient({"expenses": [_expense_row()]}))

    records = repository.list_for_business(BUSINESS_ID)

    assert len(records) == 1
    assert records[0].amount_minor_units == 350000
    assert records[0].due_date == date(2026, 11, 1)


def test_invalid_row_raises_repository_error() -> None:
    repository = BusinessRepository(FakeClient({"businesses": [{"id": "not-a-uuid"}]}))

    with pytest.raises(RepositoryError):
        repository.list_all()
