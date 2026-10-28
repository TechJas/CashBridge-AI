"""Invoice queries."""

from typing import Any
from uuid import UUID

from supabase import Client

from app.db.models import InvoiceRecord
from app.db.repositories.base import (
    execute,
    parse_int,
    parse_optional_date,
    parse_str,
    parse_uuid,
)


class InvoiceRepository:
    """Read invoices for one business from Supabase."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_for_business(self, business_id: UUID) -> list[InvoiceRecord]:
        """Return invoices owned by a business."""
        rows = execute(
            self._client.table("invoices")
            .select(
                "id,status,due_date,currency_code,"
                "total_minor_units,amount_due_minor_units"
            )
            .eq("business_id", str(business_id)),
            "Could not load invoices.",
        )
        return [self._to_record(row) for row in rows]

    @staticmethod
    def _to_record(row: dict[str, Any]) -> InvoiceRecord:
        return InvoiceRecord(
            id=parse_uuid(row, "id"),
            status=parse_str(row, "status"),
            due_date=parse_optional_date(row, "due_date"),
            currency_code=parse_str(row, "currency_code"),
            total_minor_units=parse_int(row, "total_minor_units"),
            amount_due_minor_units=parse_int(row, "amount_due_minor_units"),
        )
