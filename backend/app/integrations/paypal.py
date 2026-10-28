"""Read-only PayPal Sandbox client for invoice history."""

from typing import Any

import httpx

from app.core.config import PAYPAL_API_BASE_URL

REQUEST_TIMEOUT_SECONDS = 15.0
CONNECT_TIMEOUT_SECONDS = 5.0


class PayPalError(Exception):
    """Base error for safe PayPal failures."""


class PayPalAuthenticationError(PayPalError):
    """PayPal rejected the credentials or access token."""


class PayPalConnectionError(PayPalError):
    """PayPal could not be reached."""


class PayPalTimeoutError(PayPalError):
    """The PayPal request timed out."""


class PayPalResponseError(PayPalError):
    """PayPal returned an unexpected response."""


class PayPalClient:
    """Small PayPal client that only reads invoice data."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._transport = transport

    async def list_invoices(self, page: int, page_size: int) -> dict[str, Any]:
        """Return one page of invoices from the PayPal Sandbox."""
        timeout = httpx.Timeout(
            REQUEST_TIMEOUT_SECONDS,
            connect=CONNECT_TIMEOUT_SECONDS,
        )
        async with httpx.AsyncClient(
            base_url=PAYPAL_API_BASE_URL,
            timeout=timeout,
            transport=self._transport,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
        ) as client:
            access_token = await self._get_access_token(client)

            try:
                response = await client.get(
                    "/v2/invoicing/invoices",
                    params={"page": page, "page_size": page_size},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except httpx.TimeoutException as exc:
                raise PayPalTimeoutError("PayPal invoice request timed out.") from exc
            except httpx.RequestError as exc:
                raise PayPalConnectionError("Could not connect to PayPal.") from exc

            if response.status_code in (401, 403):
                raise PayPalAuthenticationError("PayPal rejected the access token.")
            if not response.is_success:
                raise PayPalResponseError(
                    f"PayPal invoice request returned HTTP {response.status_code}."
                )

            return self._parse_json(response)

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        """Create a short-lived OAuth 2.0 access token."""
        try:
            response = await client.post(
                "/v1/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=httpx.BasicAuth(self._client_id, self._client_secret),
            )
        except httpx.TimeoutException as exc:
            raise PayPalTimeoutError("PayPal authentication timed out.") from exc
        except httpx.RequestError as exc:
            raise PayPalConnectionError("Could not connect to PayPal.") from exc

        if response.status_code in (401, 403):
            raise PayPalAuthenticationError("PayPal rejected the client credentials.")
        if not response.is_success:
            raise PayPalResponseError(
                f"PayPal authentication returned HTTP {response.status_code}."
            )

        payload = self._parse_json(response)
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise PayPalAuthenticationError("PayPal did not return an access token.")

        return access_token

    @staticmethod
    def _parse_json(response: httpx.Response) -> dict[str, Any]:
        """Parse a JSON object without exposing response contents in errors."""
        try:
            payload = response.json()
        except ValueError as exc:
            raise PayPalResponseError("PayPal returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise PayPalResponseError("PayPal returned an unexpected response.")

        return payload
