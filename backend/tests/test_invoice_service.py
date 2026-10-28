"""Invoice service mapping checks."""

import pytest
from app.integrations.paypal import PayPalResponseError
from app.services.invoice_service import InvoiceService

PAYLOAD = {
    "total_items": 2,
    "total_pages": 1,
    "items": [
        {
            "id": "INV2-0001",
            "status": "SENT",
            "detail": {
                "invoice_number": "INV-001",
                "invoice_date": "2026-09-01",
                "currency_code": "USD",
                "payment_term": {"due_date": "2026-09-30"},
            },
            "amount": {"currency_code": "USD", "value": "125.50"},
            "due_amount": {"currency_code": "USD", "value": "125.50"},
            "primary_recipients": [
                {"billing_info": {"email_address": "payer@example.com"}}
            ],
        },
        {
            "id": "INV2-0002",
            "status": "PAID",
            "detail": {
                "invoice_number": "INV-002",
                "invoice_date": "2026-08-01",
                "due_date": "2026-08-31",
                "currency_code": "JPY",
            },
            "amount": {"currency_code": "JPY", "value": "1000"},
            "due_amount": {"currency_code": "JPY", "value": "0"},
        },
    ],
}


class FakeClient:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    async def list_invoices(self, page: int, page_size: int) -> dict:
        return self._payload


async def test_payload_is_mapped_to_safe_contract() -> None:
    service = InvoiceService(FakeClient(PAYLOAD))

    result = await service.list_invoices(page=2, page_size=25)

    assert result.page == 2
    assert result.page_size == 25
    assert result.total_items == 2
    assert result.total_pages == 1
    assert len(result.invoices) == 2

    first = result.invoices[0]
    assert first.id == "INV2-0001"
    assert first.invoice_number == "INV-001"
    assert first.due_date == "2026-09-30"
    assert first.currency_code == "USD"
    assert first.total_minor_units == 12550
    assert first.amount_due_minor_units == 12550
    assert "payer@example.com" not in result.model_dump_json()


async def test_zero_decimal_currency_is_mapped() -> None:
    service = InvoiceService(FakeClient(PAYLOAD))

    result = await service.list_invoices(page=1, page_size=10)

    assert result.invoices[1].total_minor_units == 1000


async def test_missing_items_returns_empty_page() -> None:
    service = InvoiceService(FakeClient({}))

    result = await service.list_invoices(page=1, page_size=10)

    assert result.invoices == []
    assert result.total_items is None


async def test_non_list_items_is_rejected() -> None:
    service = InvoiceService(FakeClient({"items": "unexpected"}))

    with pytest.raises(PayPalResponseError):
        await service.list_invoices(page=1, page_size=10)


async def test_invalid_amount_is_rejected() -> None:
    payload = {
        "items": [
            {
                "id": "INV2-BAD",
                "amount": {"currency_code": "USD", "value": "not-money"},
            }
        ]
    }
    service = InvoiceService(FakeClient(payload))

    with pytest.raises(PayPalResponseError):
        await service.list_invoices(page=1, page_size=10)
