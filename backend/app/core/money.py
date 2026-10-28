"""Deterministic conversion between decimal money and integer minor units."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

DEFAULT_MINOR_UNIT_EXPONENT = 2

CURRENCY_MINOR_UNIT_EXPONENTS = {
    "BHD": 3,
    "IQD": 3,
    "JOD": 3,
    "KWD": 3,
    "LYD": 3,
    "OMR": 3,
    "TND": 3,
    "CLP": 0,
    "ISK": 0,
    "JPY": 0,
    "KRW": 0,
    "VND": 0,
}


def currency_minor_unit_exponent(currency_code: str) -> int:
    """Return the number of decimal digits for an ISO 4217 currency."""
    return CURRENCY_MINOR_UNIT_EXPONENTS.get(
        currency_code.upper(), DEFAULT_MINOR_UNIT_EXPONENT
    )


def to_minor_units(amount: str | int | Decimal, currency_code: str) -> int:
    """Convert a decimal amount to integer minor units for its currency."""
    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid monetary amount.") from exc

    if not decimal_amount.is_finite():
        raise ValueError("Invalid monetary amount.")

    exponent = currency_minor_unit_exponent(currency_code)
    scale = Decimal(10) ** exponent
    return int((decimal_amount * scale).to_integral_value(rounding=ROUND_HALF_UP))
