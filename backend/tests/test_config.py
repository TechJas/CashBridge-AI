"""Configuration checks for Supabase settings."""

import pytest
from app.core.config import Settings, get_settings
from app.integrations.supabase import (
    SupabaseConfigurationError,
    create_supabase_client,
)


def test_supabase_is_not_configured_without_credentials() -> None:
    settings = Settings("", "")

    assert settings.supabase_is_configured is False


def test_supabase_is_configured_with_url_and_key() -> None:
    settings = Settings(
        "",
        "",
        supabase_url="https://example.supabase.co",
        supabase_service_role_key="test-service-role-key",
    )

    assert settings.supabase_is_configured is True


def test_get_settings_reads_supabase_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")

    settings = get_settings()

    assert settings.supabase_url == "https://example.supabase.co"
    assert settings.supabase_service_role_key == "test-service-role-key"
    assert settings.supabase_is_configured is True


def test_supabase_client_requires_configuration() -> None:
    with pytest.raises(SupabaseConfigurationError):
        create_supabase_client(Settings("", ""))
