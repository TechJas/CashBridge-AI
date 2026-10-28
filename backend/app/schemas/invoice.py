"""Invoice response contracts."""

from pydantic import BaseModel, Field


class InvoiceSummary(BaseModel):
    """Safe, minimal invoice fields needed for cash-flow planning."""

    id: str
    status: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    currency_code: str = Field(min_length=3, max_length=3)
    total_minor_units: int
    amount_due_minor_units: int


class InvoiceListResponse(BaseModel):
    """One page of invoice summaries with PayPal pagination metadata."""

    page: int
    page_size: int
    total_items: int | None = None
    total_pages: int | None = None
    invoices: list[InvoiceSummary]
