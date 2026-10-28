"""Shared repository helpers."""

from datetime import date
from typing import Any
from uuid import UUID

from app.db.errors import RepositoryError


def execute(query: Any, message: str) -> list[dict[str, Any]]:
    """Run a PostgREST query and return its rows."""
    try:
        response = query.execute()
    except Exception as exc:
        raise RepositoryError(message) from exc

    data = getattr(response, "data", None)
    if not isinstance(data, list):
        raise RepositoryError(message)
    return data


def parse_uuid(row: dict[str, Any], key: str) -> UUID:
    try:
        return UUID(str(row[key]))
    except (KeyError, TypeError, ValueError) as exc:
        raise RepositoryError("Unexpected database record.") from exc


def parse_str(row: dict[str, Any], key: str) -> str:
    try:
        value = row[key]
    except (KeyError, TypeError) as exc:
        raise RepositoryError("Unexpected database record.") from exc
    if not isinstance(value, str) or not value:
        raise RepositoryError("Unexpected database record.")
    return value


def parse_int(row: dict[str, Any], key: str) -> int:
    try:
        value = row[key]
    except (KeyError, TypeError) as exc:
        raise RepositoryError("Unexpected database record.") from exc
    if isinstance(value, bool) or not isinstance(value, int):
        raise RepositoryError("Unexpected database record.")
    return value


def parse_date(row: dict[str, Any], key: str) -> date:
    try:
        value = row[key]
    except (KeyError, TypeError) as exc:
        raise RepositoryError("Unexpected database record.") from exc
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise RepositoryError("Unexpected database record.") from exc


def parse_optional_date(row: dict[str, Any], key: str) -> date | None:
    value = row.get(key)
    if value is None:
        return None
    return parse_date(row, key)
