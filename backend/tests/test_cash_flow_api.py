"""Local cash-flow and business API tests."""

from datetime import date
from uuid import UUID

import pytest
from app.api import dependencies
from app.api.dependencies import get_business_service, get_cash_flow_service
from app.db.errors import RepositoryError
from app.integrations.supabase import SupabaseConfigurationError
from app.main import app
from app.schemas.cash_flow import (
    BusinessSummary,
    CashFlowHorizon,
    CashFlowSummary,
)
from app.services.cash_flow import CurrencyMismatchError
from app.services.cash_flow_service import BusinessNotFoundError
from fastapi.testclient import TestClient

BUSINESS_ID = UUID("11111111-1111-4111-8111-111111111111")
AS_OF = date(2026, 10, 28)

SUMMARY = CashFlowSummary(
    business_id=BUSINESS_ID,
    business_name="Bridgewater Design Studio",
    currency_code="USD",
    as_of=AS_OF,
    collected_minor_units=250000,
    outstanding_receivables_minor_units=1150000,
    overdue_receivables_minor_units=270000,
    planned_expenses_minor_units=607000,
    overdue_expenses_minor_units=350000,
    open_invoice_count=5,
    overdue_invoice_count=2,
    planned_expense_count=4,
    horizons=[
        CashFlowHorizon(
            days=30,
            through=date(2026, 11, 27),
            expected_inflow_minor_units=750000,
            expected_outflow_minor_units=362000,
            net_cash_flow_minor_units=388000,
        )
    ],
)

BUSINESS_SUMMARY = BusinessSummary(
    id=BUSINESS_ID,
    name="Bridgewater Design Studio",
    base_currency="USD",
)


class FakeBusinessService:
    async def list_businesses(self) -> list[BusinessSummary]:
        return [BUSINESS_SUMMARY]


class FailingBusinessService:
    async def list_businesses(self) -> list[BusinessSummary]:
        raise RepositoryError("database unavailable")


class FakeCashFlowService:
    async def summarize(
        self, business_id: UUID, as_of: date | None = None
    ) -> CashFlowSummary:
        if business_id != BUSINESS_ID:
            raise BusinessNotFoundError("missing")
        if as_of is not None:
            return SUMMARY.model_copy(update={"as_of": as_of})
        return SUMMARY


class MissingCashFlowService:
    async def summarize(
        self, business_id: UUID, as_of: date | None = None
    ) -> CashFlowSummary:
        raise BusinessNotFoundError("missing")


class CurrencyMismatchService:
    async def summarize(
        self, business_id: UUID, as_of: date | None = None
    ) -> CashFlowSummary:
        raise CurrencyMismatchError("mixed currency")


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_list_businesses(client: TestClient) -> None:
    app.dependency_overrides[get_business_service] = lambda: FakeBusinessService()

    response = client.get("/api/businesses")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(BUSINESS_ID),
            "name": "Bridgewater Design Studio",
            "base_currency": "USD",
        }
    ]


def test_business_repository_failure_returns_502(client: TestClient) -> None:
    app.dependency_overrides[get_business_service] = lambda: FailingBusinessService()

    response = client.get("/api/businesses")

    assert response.status_code == 502


def test_cash_flow_summary_returns_values(client: TestClient) -> None:
    app.dependency_overrides[get_cash_flow_service] = lambda: FakeCashFlowService()

    response = client.get(
        f"/api/cash-flow/summary?business_id={BUSINESS_ID}&as_of=2026-10-28"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["collected_minor_units"] == 250000
    assert body["outstanding_receivables_minor_units"] == 1150000
    assert body["overdue_receivables_minor_units"] == 270000
    assert body["as_of"] == "2026-10-28"
    assert body["horizons"][0]["net_cash_flow_minor_units"] == 388000


def test_unknown_business_returns_404(client: TestClient) -> None:
    app.dependency_overrides[get_cash_flow_service] = lambda: MissingCashFlowService()

    response = client.get(f"/api/cash-flow/summary?business_id={BUSINESS_ID}")

    assert response.status_code == 404


def test_currency_mismatch_returns_409(client: TestClient) -> None:
    app.dependency_overrides[get_cash_flow_service] = lambda: CurrencyMismatchService()

    response = client.get(f"/api/cash-flow/summary?business_id={BUSINESS_ID}")

    assert response.status_code == 409


def test_unconfigured_supabase_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_configuration_error():
        raise SupabaseConfigurationError("missing")

    monkeypatch.setattr(
        dependencies,
        "create_supabase_client",
        raise_configuration_error,
    )

    response = client.get("/api/businesses")

    assert response.status_code == 503
    assert response.json() == {"detail": "Supabase is not configured."}


def test_remote_client_is_rejected() -> None:
    with TestClient(app, client=("203.0.113.10", 12345)) as remote_client:
        response = remote_client.get("/api/businesses")

    assert response.status_code == 403


def test_openapi_contains_local_finance_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/businesses" in paths
    assert "/api/cash-flow/summary" in paths
