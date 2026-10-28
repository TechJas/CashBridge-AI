"""Cash-flow response contracts."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class BusinessSummary(BaseModel):
    """A business available for local development."""

    id: UUID
    name: str
    base_currency: str = Field(min_length=3, max_length=3)


class CashFlowHorizon(BaseModel):
    """Cumulative expected cash movement through a future date."""

    days: int = Field(ge=1)
    through: date
    expected_inflow_minor_units: int = Field(ge=0)
    expected_outflow_minor_units: int = Field(ge=0)
    net_cash_flow_minor_units: int


class CashFlowSummary(BaseModel):
    """Deterministic cash-flow position for one business."""

    business_id: UUID
    business_name: str
    currency_code: str = Field(min_length=3, max_length=3)
    as_of: date
    collected_minor_units: int = Field(ge=0)
    outstanding_receivables_minor_units: int = Field(ge=0)
    overdue_receivables_minor_units: int = Field(ge=0)
    planned_expenses_minor_units: int = Field(ge=0)
    overdue_expenses_minor_units: int = Field(ge=0)
    open_invoice_count: int = Field(ge=0)
    overdue_invoice_count: int = Field(ge=0)
    planned_expense_count: int = Field(ge=0)
    horizons: list[CashFlowHorizon]
