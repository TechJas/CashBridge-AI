"""PayPal client checks against a mocked HTTP transport."""

import httpx
import pytest
from app.integrations.paypal import (
    PayPalAuthenticationError,
    PayPalClient,
    PayPalConnectionError,
    PayPalResponseError,
    PayPalTimeoutError,
)

INVOICE_PAYLOAD = {
    "total_items": 1,
    "total_pages": 1,
    "items": [{"id": "INV2-TEST", "status": "SENT"}],
}


def _token_response() -> httpx.Response:
    return httpx.Response(200, json={"access_token": "test-token"})


async def test_list_invoices_authenticates_and_forwards_pagination() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            seen["token_authorization"] = request.headers.get("authorization")
            return _token_response()

        seen["authorization"] = request.headers.get("authorization")
        seen["page"] = request.url.params["page"]
        seen["page_size"] = request.url.params["page_size"]
        return httpx.Response(200, json=INVOICE_PAYLOAD)

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    payload = await client.list_invoices(page=2, page_size=25)

    assert payload == INVOICE_PAYLOAD
    assert str(seen["token_authorization"]).startswith("Basic ")
    assert seen["authorization"] == "Bearer test-token"
    assert seen["page"] == "2"
    assert seen["page_size"] == "25"


async def test_invoice_request_uses_bearer_token() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return _token_response()
        seen["authorization"] = request.headers["authorization"]
        return httpx.Response(200, json=INVOICE_PAYLOAD)

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    await client.list_invoices(page=1, page_size=10)

    assert seen["authorization"] == "Bearer test-token"


async def test_authentication_failure_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid_client"})

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalAuthenticationError):
        await client.list_invoices(page=1, page_size=10)


async def test_invoice_authentication_failure_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return _token_response()
        return httpx.Response(403, json={"error": "forbidden"})

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalAuthenticationError):
        await client.list_invoices(page=1, page_size=10)


async def test_timeout_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return _token_response()
        raise httpx.ReadTimeout("timed out", request=request)

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalTimeoutError):
        await client.list_invoices(page=1, page_size=10)


async def test_connection_failure_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("unreachable", request=request)

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalConnectionError):
        await client.list_invoices(page=1, page_size=10)


async def test_upstream_error_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return _token_response()
        return httpx.Response(500, json={"message": "boom"})

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalResponseError):
        await client.list_invoices(page=1, page_size=10)


async def test_missing_access_token_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"scope": "invoices.read"})

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalAuthenticationError):
        await client.list_invoices(page=1, page_size=10)


async def test_invalid_json_is_mapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return _token_response()
        return httpx.Response(
            200,
            content=b"not-json",
            headers={"content-type": "application/json"},
        )

    client = PayPalClient(
        "client-id",
        "client-secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(PayPalResponseError):
        await client.list_invoices(page=1, page_size=10)
