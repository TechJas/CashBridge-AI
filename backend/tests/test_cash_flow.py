"""Deterministic cash-flow calculation tests."""

from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest
from app.db.models import BusinessRecord, ExpenseRecord, InvoiceRecord
from app.services.cash_flow import CurrencyMismatchError, calculate_cash_flow

BUSINESS = BusinessRecord(
    id=UUID("11111111-1111-4111-8111-111111111111"),
    name="Bridgewater Design Studio",
    base_currency="USD",
)
AS_OF = date(2026, 10, 28)


def _invoice(
    status: str,
    total: int,
    due: int,
    due_date: date | None,
    currency: str = "USD",
) -> InvoiceRecord:
    return InvoiceRecord(
        id=UUID(int=len(status) + total),
        status=status,
        due_date=due_date,
        currency_code=currency,
        total_minor_units=total,
        amount_due_minor_units=due,
    )


def _expense(
    status: str,
    amount: int,
    due_date: date,
    currency: str = "USD",
) -> ExpenseRecord:
    return ExpenseRecord(
        id=UUID(int=amount),
        status=status,
        due_date=due_date,
        currency_code=currency,
        amount_minor_units=amount,
    )


def _invoices() -> list[InvoiceRecord]:
    return [
        _invoice("PAID", 100000, 0, date(2026, 9, 15)),
        _invoice("PARTIALLY_PAID", 300000, 150000, date(2026, 10, 20)),
        _invoice("SENT", 120000, 120000, date(2026, 10, 15)),
        _invoice("SENT", 480000, 480000, date(2026, 11, 5)),
        _invoice("SENT", 240000, 240000, date(2026, 12, 10)),
        _invoice("SENT", 160000, 160000, date(2027, 1, 20)),
        _invoice("DRAFT", 90000, 90000, date(2026, 11, 10)),
        _invoice("CANCELLED", 50000, 0, date(2026, 10, 1)),
    ]


def _expenses() -> list[ExpenseRecord]:
    return [
        _expense("planned", 350000, date(2026, 10, 25)),
        _expense("planned", 12000, date(2026, 11, 2)),
        _expense("planned", 200000, date(2026, 12, 15)),
        _expense("planned", 45000, date(2027, 1, 15)),
        _expense("paid", 99999, date(2026, 10, 1)),
    ]


def test_paid_and_partially_paid_invoices_are_collected_cash() -> None:
    summary = calculate_cash_flow(BUSINESS, _invoices(), _expenses(), AS_OF)

    assert summary.collected_minor_units == 250000


def test_unpaid_invoices_are_not_counted_as_collected() -> None:
    invoices = [_invoice("SENT", 50000, 50000, date(2026, 11, 1))]

    summary = calculate_cash_flow(BUSINESS, invoices, [], AS_OF)

    assert summary.collected_minor_units == 0
    assert summary.outstanding_receivables_minor_units == 50000


def test_draft_invoices_are_not_receivables() -> None:
    invoices = [_invoice("DRAFT", 90000, 90000, date(2026, 11, 1))]

    summary = calculate_cash_flow(BUSINESS, invoices, [], AS_OF)

    assert summary.outstanding_receivables_minor_units == 0
    assert summary.horizons[0].expected_inflow_minor_units == 0


def test_receivable_position_and_overdue_invoices() -> None:
    summary = calculate_cash_flow(BUSINESS, _invoices(), _expenses(), AS_OF)

    assert summary.outstanding_receivables_minor_units == 1150000
    assert summary.overdue_receivables_minor_units == 270000
    assert summary.open_invoice_count == 5
    assert summary.overdue_invoice_count == 2


def test_expense_position_and_overdue_expenses() -> None:
    summary = calculate_cash_flow(BUSINESS, _invoices(), _expenses(), AS_OF)

    assert summary.planned_expenses_minor_units == 607000
    assert summary.overdue_expenses_minor_units == 350000
    assert summary.planned_expense_count == 4


def test_cumulative_horizons_include_overdue_items() -> None:
    summary = calculate_cash_flow(BUSINESS, _invoices(), _expenses(), AS_OF)

    thirty, sixty, ninety = summary.horizons

    assert thirty.through == date(2026, 11, 27)
    assert thirty.expected_inflow_minor_units == 750000
    assert thirty.expected_outflow_minor_units == 362000
    assert thirty.net_cash_flow_minor_units == 388000

    assert sixty.through == date(2026, 12, 27)
    assert sixty.expected_inflow_minor_units == 990000
    assert sixty.expected_outflow_minor_units == 562000
    assert sixty.net_cash_flow_minor_units == 428000

    assert ninety.through == date(2027, 1, 26)
    assert ninety.expected_inflow_minor_units == 1150000
    assert ninety.expected_outflow_minor_units == 607000
    assert ninety.net_cash_flow_minor_units == 543000


def test_empty_business_returns_zeroes() -> None:
    summary = calculate_cash_flow(BUSINESS, [], [], AS_OF)

    assert summary.collected_minor_units == 0
    assert summary.outstanding_receivables_minor_units == 0
    assert summary.planned_expenses_minor_units == 0
    assert all(horizon.net_cash_flow_minor_units == 0 for horizon in summary.horizons)


def test_large_integers_remain_exact() -> None:
    first = 9007199254740993
    invoices = [
        _invoice("PAID", first, 0, None),
        _invoice("PAID", 1, 0, None),
    ]

    summary = calculate_cash_flow(BUSINESS, invoices, [], AS_OF)

    assert summary.collected_minor_units == first + 1
    assert summary.collected_minor_units == int(Decimal(first) + Decimal(1))


@pytest.mark.parametrize(
    "record",
    [
        _invoice("SENT", 1000, 1000, date(2026, 11, 1), currency="EUR"),
        _expense("planned", 1000, date(2026, 11, 1), currency="EUR"),
    ],
)
def test_currency_mismatch_is_rejected(record) -> None:
    invoices = [record] if isinstance(record, InvoiceRecord) else []
    expenses = [record] if isinstance(record, ExpenseRecord) else []

    with pytest.raises(CurrencyMismatchError):
        calculate_cash_flow(BUSINESS, invoices, expenses, AS_OF)
