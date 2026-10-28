"""Server-side Supabase client setup."""

from supabase import Client, create_client

from app.core.config import Settings, get_settings


class SupabaseConfigurationError(Exception):
    """Supabase credentials are missing."""


def create_supabase_client(settings: Settings | None = None) -> Client:
    """Create a service-role Supabase client for backend use only."""
    resolved = settings or get_settings()
    if not resolved.supabase_is_configured:
        raise SupabaseConfigurationError("Supabase credentials are not configured.")

    return create_client(
        resolved.supabase_url,
        resolved.supabase_service_role_key,
    )
