"""API behavior for the invoice endpoint."""

from collections.abc import Callable
from typing import Any

import pytest
from app.api import invoices as invoices_module
from app.core.config import Settings
from app.integrations.paypal import (
    PayPalAuthenticationError,
    PayPalConnectionError,
    PayPalError,
    PayPalResponseError,
    PayPalTimeoutError,
)
from fastapi.testclient import TestClient

PAYLOAD = {
    "total_items": 1,
    "total_pages": 1,
    "items": [
        {
            "id": "INV2-0001",
            "status": "SENT",
            "detail": {
                "invoice_number": "INV-001",
                "invoice_date": "2026-09-01",
                "due_date": "2026-09-30",
                "currency_code": "USD",
            },
            "amount": {"currency_code": "USD", "value": "125.50"},
            "due_amount": {"currency_code": "USD", "value": "125.50"},
            "primary_recipients": [
                {"billing_info": {"email_address": "payer@example.com"}}
            ],
        }
    ],
}


def _configure(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    error_factory: Callable[[], Exception] | None = None,
) -> None:
    class FakePayPalClient:
        def __init__(self, client_id: str, client_secret: str) -> None:
            self.client_id = client_id
            self.client_secret = client_secret

        async def list_invoices(self, page: int, page_size: int) -> dict[str, Any]:
            if error_factory is not None:
                raise error_factory()
            return PAYLOAD

    monkeypatch.setattr(invoices_module, "get_settings", lambda: settings)
    monkeypatch.setattr(invoices_module, "PayPalClient", FakePayPalClient)


def test_missing_credentials_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _configure(monkeypatch, Settings("", ""))

    response = client.get("/api/invoices")

    assert response.status_code == 503
    assert response.json() == {"detail": "PayPal credentials are not configured."}


@pytest.mark.parametrize(
    ("query",),
    [("page=0",), ("page=-1",), ("page_size=0",), ("page_size=101",)],
)
def test_pagination_validation_returns_422(client: TestClient, query: str) -> None:
    response = client.get(f"/api/invoices?{query}")

    assert response.status_code == 422


def test_invoice_page_is_returned(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _configure(monkeypatch, Settings("client-id", "client-secret"))

    response = client.get("/api/invoices?page=2&page_size=25")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["page_size"] == 25
    assert body["total_items"] == 1
    assert body["invoices"][0]["id"] == "INV2-0001"
    assert body["invoices"][0]["total_minor_units"] == 12550
    assert "payer@example.com" not in response.text


@pytest.mark.parametrize(
    ("error_factory", "expected_status"),
    [
        (PayPalTimeoutError, 504),
        (PayPalAuthenticationError, 502),
        (PayPalConnectionError, 502),
        (PayPalResponseError, 502),
        (PayPalError, 502),
    ],
)
def test_paypal_errors_are_mapped_to_safe_responses(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    error_factory: Callable[[], Exception],
    expected_status: int,
) -> None:
    _configure(
        monkeypatch,
        Settings("client-id", "client-secret"),
        error_factory=error_factory,
    )

    response = client.get("/api/invoices")

    assert response.status_code == expected_status
    assert "client-secret" not in response.text
    assert "Bearer" not in response.text


def test_openapi_contains_invoice_contract(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert "/api/invoices" in schema["paths"]
    response_schema = schema["paths"]["/api/invoices"]["get"]["responses"]["200"]
    assert "InvoiceListResponse" in str(response_schema)
