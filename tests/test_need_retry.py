import pytest
from httpx import (
    HTTPStatusError,
    Request,
    Response,
    TimeoutException,
)

from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.utils import ChaturbateUtils


class TestNeedRetry:
    """Tests for the need_retry function."""

    @pytest.mark.parametrize(
        ("status_code", "expected"),
        [
            (HttpStatusCode.INTERNAL_SERVER_ERROR, True),
            (HttpStatusCode.BAD_GATEWAY, True),
            (HttpStatusCode.SERVICE_UNAVAILABLE, True),
            (HttpStatusCode.GATEWAY_TIMEOUT, True),
            (HttpStatusCode.BAD_REQUEST, False),
            (HttpStatusCode.UNAUTHORIZED, False),
            (HttpStatusCode.FORBIDDEN, False),
            (HttpStatusCode.NOT_FOUND, False),
        ],
    )
    def test_http_status_error(self, status_code: int, expected: bool) -> None:
        """Test need_retry with HTTPStatusError exceptions."""
        exception = HTTPStatusError(
            message="Error",
            request=Request("GET", "https://error.url.com"),
            response=Response(status_code),
        )
        assert ChaturbateUtils().need_retry(exception) == expected

    def test_non_http_status_error(self) -> None:
        """Test need_retry with a non-HTTPStatusError exception."""
        exception = TimeoutException("Timeout occurred")
        assert not ChaturbateUtils().need_retry(exception)
