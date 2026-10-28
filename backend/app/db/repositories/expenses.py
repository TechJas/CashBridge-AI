"""Expense queries."""

from typing import Any
from uuid import UUID

from supabase import Client

from app.db.models import ExpenseRecord
from app.db.repositories.base import (
    execute,
    parse_date,
    parse_int,
    parse_str,
    parse_uuid,
)


class ExpenseRepository:
    """Read expenses for one business from Supabase."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_for_business(self, business_id: UUID) -> list[ExpenseRecord]:
        """Return expenses owned by a business."""
        rows = execute(
            self._client.table("expenses")
            .select("id,status,due_date,currency_code,amount_minor_units")
            .eq("business_id", str(business_id)),
            "Could not load expenses.",
        )
        return [self._to_record(row) for row in rows]

    @staticmethod
    def _to_record(row: dict[str, Any]) -> ExpenseRecord:
        return ExpenseRecord(
            id=parse_uuid(row, "id"),
            status=parse_str(row, "status"),
            due_date=parse_date(row, "due_date"),
            currency_code=parse_str(row, "currency_code"),
            amount_minor_units=parse_int(row, "amount_minor_units"),
        )
