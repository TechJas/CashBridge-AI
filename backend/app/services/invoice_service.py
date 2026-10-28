"""Invoice history orchestration and response mapping."""

from typing import Any

from app.core.money import to_minor_units
from app.integrations.paypal import PayPalClient, PayPalResponseError
from app.schemas.invoice import InvoiceListResponse, InvoiceSummary


class InvoiceService:
    """Turn raw PayPal invoice data into a safe application contract."""

    def __init__(self, client: PayPalClient) -> None:
        self._client = client

    async def list_invoices(self, page: int, page_size: int) -> InvoiceListResponse:
        """Return one page of invoice summaries."""
        payload = await self._client.list_invoices(page=page, page_size=page_size)
        return self._build_response(payload, page=page, page_size=page_size)

    def _build_response(
        self,
        payload: dict[str, Any],
        page: int,
        page_size: int,
    ) -> InvoiceListResponse:
        items = payload.get("items")
        if items is None:
            items = []
        if not isinstance(items, list):
            raise PayPalResponseError("PayPal returned an unexpected invoice list.")

        invoices = [
            self._build_invoice(item)
            for item in items
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]

        return InvoiceListResponse(
            page=page,
            page_size=page_size,
            total_items=self._optional_int(payload.get("total_items")),
            total_pages=self._optional_int(payload.get("total_pages")),
            invoices=invoices,
        )

    def _build_invoice(self, item: dict[str, Any]) -> InvoiceSummary:
        detail = item.get("detail")
        if not isinstance(detail, dict):
            detail = {}

        amount = item.get("amount")
        if not isinstance(amount, dict):
            amount = {}

        due_amount = item.get("due_amount")
        if not isinstance(due_amount, dict):
            due_amount = {}

        currency_code = (
            amount.get("currency_code")
            or detail.get("currency_code")
            or due_amount.get("currency_code")
            or "USD"
        )
        currency_code = str(currency_code).upper()

        return InvoiceSummary(
            id=item["id"],
            status=self._optional_str(item.get("status")),
            invoice_number=self._optional_str(detail.get("invoice_number")),
            invoice_date=self._optional_str(detail.get("invoice_date")),
            due_date=self._optional_str(detail.get("due_date")),
            currency_code=currency_code,
            total_minor_units=self._money(amount.get("value"), currency_code),
            amount_due_minor_units=self._money(due_amount.get("value"), currency_code),
        )

    @staticmethod
    def _money(value: Any, currency_code: str) -> int:
        if value is None or value == "":
            return 0
        try:
            return to_minor_units(value, currency_code)
        except ValueError as exc:
            raise PayPalResponseError("PayPal returned an invalid amount.") from exc

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if isinstance(value, bool) or value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
