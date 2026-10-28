"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PAYPAL_API_BASE_URL = "https://api-m.sandbox.paypal.com"

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


DEFAULT_FRONTEND_ORIGIN = "http://localhost:5173"


@dataclass(frozen=True)
class Settings:
    """Configuration required by the PayPal integration."""

    paypal_client_id: str
    paypal_client_secret: str
    frontend_origin: str = DEFAULT_FRONTEND_ORIGIN

    @property
    def paypal_is_configured(self) -> bool:
        """Return True when both PayPal credentials are present."""
        return bool(self.paypal_client_id and self.paypal_client_secret)


def get_settings() -> Settings:
    """Read settings from environment variables."""
    return Settings(
        paypal_client_id=os.getenv("PAYPAL_CLIENT_ID", "").strip(),
        paypal_client_secret=os.getenv("PAYPAL_CLIENT_SECRET", "").strip(),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", DEFAULT_FRONTEND_ORIGIN).strip()
        or DEFAULT_FRONTEND_ORIGIN,
    )
