"""Typed database records used by the service layer."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class BusinessRecord:
    """A business owned by the current tenant."""

    id: UUID
    name: str
    base_currency: str


@dataclass(frozen=True)
class InvoiceRecord:
    """The invoice fields needed for cash-flow calculations."""

    id: UUID
    status: str
    due_date: date | None
    currency_code: str
    total_minor_units: int
    amount_due_minor_units: int


@dataclass(frozen=True)
class ExpenseRecord:
    """The expense fields needed for cash-flow calculations."""

    id: UUID
    status: str
    due_date: date
    currency_code: str
    amount_minor_units: int
