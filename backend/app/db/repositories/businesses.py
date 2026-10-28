"""Business queries."""

from typing import Any
from uuid import UUID

from supabase import Client

from app.db.models import BusinessRecord
from app.db.repositories.base import execute, parse_str, parse_uuid


class BusinessRepository:
    """Read businesses from Supabase."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list_all(self) -> list[BusinessRecord]:
        """Return every business, ordered by name."""
        rows = execute(
            self._client.table("businesses")
            .select("id,name,base_currency")
            .order("name"),
            "Could not load businesses.",
        )
        return [self._to_record(row) for row in rows]

    def get(self, business_id: UUID) -> BusinessRecord | None:
        """Return one business by ID, or None when it does not exist."""
        rows = execute(
            self._client.table("businesses")
            .select("id,name,base_currency")
            .eq("id", str(business_id))
            .limit(1),
            "Could not load the business.",
        )
        if not rows:
            return None
        return self._to_record(rows[0])

    @staticmethod
    def _to_record(row: dict[str, Any]) -> BusinessRecord:
        return BusinessRecord(
            id=parse_uuid(row, "id"),
            name=parse_str(row, "name"),
            base_currency=parse_str(row, "base_currency"),
        )
