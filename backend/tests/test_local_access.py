"""Local-only access guard tests."""

import pytest
from app.api.dependencies import require_local_access
from fastapi import HTTPException
from starlette.requests import Request


def _request(host: str) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": (host, 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
    )


@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "::1", "::ffff:127.0.0.1", "localhost", "testclient"],
)
def test_local_hosts_are_allowed(host: str) -> None:
    require_local_access(_request(host))


def test_remote_host_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_local_access(_request("203.0.113.10"))

    assert exc_info.value.status_code == 403
