"""Health and CORS checks."""

from app.core.config import get_settings
from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "cashbridge-api"}


def test_cors_allows_configured_frontend_origin(client: TestClient) -> None:
    origin = get_settings().frontend_origin
    response = client.options(
        "/api/invoices",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
