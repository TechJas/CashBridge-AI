"""Deterministic cash-flow calculations."""

from collections.abc import Sequence
from datetime import date, timedelta
from decimal import Decimal

from app.db.models import BusinessRecord, ExpenseRecord, InvoiceRecord
from app.schemas.cash_flow import CashFlowHorizon, CashFlowSummary

COLLECTED_INVOICE_STATUSES = frozenset({"PAID", "MARKED_AS_PAID", "PARTIALLY_PAID"})
OPEN_INVOICE_STATUSES = frozenset({"SENT", "SCHEDULED", "PARTIALLY_PAID"})
PLANNED_EXPENSE_STATUS = "planned"
HORIZONS_DAYS = (30, 60, 90)


class CurrencyMismatchError(Exception):
    """A record uses a currency other than the business base currency."""


def calculate_cash_flow(
    business: BusinessRecord,
    invoices: Sequence[InvoiceRecord],
    expenses: Sequence[ExpenseRecord],
    as_of: date,
) -> CashFlowSummary:
    """Calculate the current position and cumulative 30/60/90 day outlook."""
    currency_code = business.base_currency.upper()
    _ensure_single_currency(currency_code, invoices, expenses)

    collected = sum(
        (
            Decimal(max(invoice.total_minor_units - invoice.amount_due_minor_units, 0))
            for invoice in invoices
            if invoice.status in COLLECTED_INVOICE_STATUSES
        ),
        Decimal("0"),
    )

    open_invoices = [
        invoice
        for invoice in invoices
        if invoice.status in OPEN_INVOICE_STATUSES
        and invoice.amount_due_minor_units > 0
    ]
    overdue_invoices = [
        invoice
        for invoice in open_invoices
        if invoice.due_date is not None and invoice.due_date < as_of
    ]
    outstanding = sum(
        (Decimal(invoice.amount_due_minor_units) for invoice in open_invoices),
        Decimal("0"),
    )
    overdue_receivables = sum(
        (Decimal(invoice.amount_due_minor_units) for invoice in overdue_invoices),
        Decimal("0"),
    )

    planned_expenses = [
        expense for expense in expenses if expense.status == PLANNED_EXPENSE_STATUS
    ]
    overdue_expenses = [
        expense for expense in planned_expenses if expense.due_date < as_of
    ]
    planned_total = sum(
        (Decimal(expense.amount_minor_units) for expense in planned_expenses),
        Decimal("0"),
    )
    overdue_expense_total = sum(
        (Decimal(expense.amount_minor_units) for expense in overdue_expenses),
        Decimal("0"),
    )

    horizons = [
        _build_horizon(days, as_of, open_invoices, planned_expenses)
        for days in HORIZONS_DAYS
    ]

    return CashFlowSummary(
        business_id=business.id,
        business_name=business.name,
        currency_code=currency_code,
        as_of=as_of,
        collected_minor_units=_as_int(collected),
        outstanding_receivables_minor_units=_as_int(outstanding),
        overdue_receivables_minor_units=_as_int(overdue_receivables),
        planned_expenses_minor_units=_as_int(planned_total),
        overdue_expenses_minor_units=_as_int(overdue_expense_total),
        open_invoice_count=len(open_invoices),
        overdue_invoice_count=len(overdue_invoices),
        planned_expense_count=len(planned_expenses),
        horizons=horizons,
    )


def _build_horizon(
    days: int,
    as_of: date,
    open_invoices: Sequence[InvoiceRecord],
    planned_expenses: Sequence[ExpenseRecord],
) -> CashFlowHorizon:
    through = as_of + timedelta(days=days)

    inflow = sum(
        (
            Decimal(invoice.amount_due_minor_units)
            for invoice in open_invoices
            if invoice.due_date is not None and invoice.due_date <= through
        ),
        Decimal("0"),
    )
    outflow = sum(
        (
            Decimal(expense.amount_minor_units)
            for expense in planned_expenses
            if expense.due_date <= through
        ),
        Decimal("0"),
    )

    inflow_minor_units = _as_int(inflow)
    outflow_minor_units = _as_int(outflow)

    return CashFlowHorizon(
        days=days,
        through=through,
        expected_inflow_minor_units=inflow_minor_units,
        expected_outflow_minor_units=outflow_minor_units,
        net_cash_flow_minor_units=inflow_minor_units - outflow_minor_units,
    )


def _ensure_single_currency(
    currency_code: str,
    invoices: Sequence[InvoiceRecord],
    expenses: Sequence[ExpenseRecord],
) -> None:
    currencies = {record.currency_code.upper() for record in (*invoices, *expenses)}
    if currencies and currencies != {currency_code}:
        raise CurrencyMismatchError("All records must use the business base currency.")


def _as_int(amount: Decimal) -> int:
    return int(amount.to_integral_value())
