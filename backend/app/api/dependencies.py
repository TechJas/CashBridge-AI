"""Shared API dependencies."""

from fastapi import HTTPException, Request
from supabase import Client

from app.db.repositories.businesses import BusinessRepository
from app.db.repositories.expenses import ExpenseRepository
from app.db.repositories.invoices import InvoiceRepository
from app.integrations.supabase import (
    SupabaseConfigurationError,
    create_supabase_client,
)
from app.services.business_service import BusinessService
from app.services.cash_flow_service import CashFlowService

LOCAL_CLIENT_HOSTS = frozenset(
    {"127.0.0.1", "::1", "::ffff:127.0.0.1", "localhost", "testclient"}
)


def require_local_access(request: Request) -> None:
    """Reject financial-data requests that do not come from this machine."""
    client = request.client
    host = client.host if client is not None else ""
    if host not in LOCAL_CLIENT_HOSTS:
        raise HTTPException(
            status_code=403,
            detail="Financial endpoints are available only from the local machine.",
        )


def get_business_service() -> BusinessService:
    """Build the business service with a service-role Supabase client."""
    return BusinessService(BusinessRepository(_supabase_client()))


def get_cash_flow_service() -> CashFlowService:
    """Build the cash-flow service with a service-role Supabase client."""
    client = _supabase_client()
    return CashFlowService(
        businesses=BusinessRepository(client),
        invoices=InvoiceRepository(client),
        expenses=ExpenseRepository(client),
    )


def _supabase_client() -> Client:
    try:
        return create_supabase_client()
    except SupabaseConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured.",
        ) from exc
