"""Money conversion checks."""

from decimal import Decimal

import pytest
from app.core.money import currency_minor_unit_exponent, to_minor_units


def test_usd_is_converted_to_cents() -> None:
    assert to_minor_units("125.50", "USD") == 12550


def test_decimal_input_is_supported() -> None:
    assert to_minor_units(Decimal("0.99"), "EUR") == 99


def test_zero_decimal_currency_is_not_scaled() -> None:
    assert to_minor_units("1000", "JPY") == 1000


def test_three_decimal_currency_is_scaled() -> None:
    assert to_minor_units("1.234", "KWD") == 1234


def test_unknown_currency_defaults_to_two_decimals() -> None:
    assert currency_minor_unit_exponent("USD") == 2


@pytest.mark.parametrize("amount", ["", "not-a-number", "NaN", "Infinity"])
def test_invalid_amounts_are_rejected(amount: str) -> None:
    with pytest.raises(ValueError):
        to_minor_units(amount, "USD")
