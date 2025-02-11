import logging
from typing import Any

import pytest
from httpx import HTTPStatusError, Request, Response

from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.utils.helpers import ChaturbateUtils


class TestUtils:
    """Tests for the utility functions."""

    @pytest.mark.parametrize(
        ("wait", "tries", "expected_log"),
        [
            (1.0, 1, "Backing off for 1 seconds after 1 tries."),
            (2.0, 3, "Backing off for 2 seconds after 3 tries."),
        ],
    )
    def test_backoff_handler(self, caplog: Any, wait: float, tries: int, expected_log: str) -> None:
        """Test backoff handler logging."""
        caplog.set_level(logging.INFO)
        ChaturbateUtils().backoff_handler({
            "wait": wait,
            "tries": tries,
            "target": lambda: None,
            "elapsed": 0,
            "args": (),
            "kwargs": {},
        })
        assert expected_log in caplog.text

    @pytest.mark.parametrize(
        ("status_code", "error_message"),
        [
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
        ],
    )
    def test_giveup_handler_server_errors(
        self, caplog: Any, status_code: int, error_message: str
    ) -> None:
        """Test giveup handler with server error status codes."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match=r"Unhandled polling error encountered."):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 3,
                "exception": HTTPStatusError(  # mypy: ignore[call-arg]  # type: ignore[call-arg]
                    message=error_message,
                    request=Request("GET", "https://error.url.com"),
                    response=Response(status_code),
                ),
            })
        assert (
            f"Giving up after 3 tries. Last error: {error_message}. Status code: {status_code}"
        ) in caplog.text

    @pytest.mark.parametrize(
        ("http_code", "expected_message"),
        [
            (400, "Unhandled polling error encountered."),
            (401, "Invalid token or unauthorized access."),
            (403, "Access forbidden. Check credentials."),
            (404, "Resource not found."),
        ],
    )
    def test_giveup_handler_no_retry(
        self, caplog: Any, http_code: int, expected_message: str
    ) -> None:
        """Test giveup handler without retry for client errors."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match=expected_message):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 1,
                "exception": HTTPStatusError(  # mypy: ignore[call-arg]  # type: ignore[call-arg]
                    message="Client Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(http_code),
                ),
            })
        assert (
            f"Giving up after 1 tries. Last error: Client Error. Status code: {http_code}"
        ) in caplog.text

    def test_giveup_handler_no_exception(self, caplog: Any) -> None:
        """Test giveup handler when no exception is present."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match=r"Unhandled polling error encountered."):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 6,
                "exception": HTTPStatusError(  # mypy: ignore[call-arg]  # type: ignore[call-arg]
                    message="Unknown Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(500),
                ),
            })
        assert "Giving up after 6 tries. Last error: Unknown Error. Status code: 500" in caplog.text

    def test_need_retry_with_retryable_status_codes(self) -> None:
        """Test need_retry function with retryable status codes."""
        retryable_status_codes = [
            HttpStatusCode.INTERNAL_SERVER_ERROR,  # 500
            HttpStatusCode.BAD_GATEWAY,  # 502
            HttpStatusCode.SERVICE_UNAVAILABLE,  # 503
            HttpStatusCode.GATEWAY_TIMEOUT,  # 504
            HttpStatusCode.CLOUDFLARE_ERROR,  # 520
            HttpStatusCode.WEB_SERVER_IS_DOWN,  # 521
        ]

        for status_code in retryable_status_codes:
            response = Response(status_code=status_code)
            request = Request("GET", "http://testserver")
            exception = HTTPStatusError(message="", request=request, response=response)
            assert ChaturbateUtils.need_retry(exception) is True

    def test_need_retry_with_non_retryable_status_codes(self) -> None:
        """Test need_retry function with non-retryable status codes."""
        non_retryable_status_codes = [
            HttpStatusCode.OK,  # 200
            HttpStatusCode.BAD_REQUEST,  # 400
            HttpStatusCode.UNAUTHORIZED,  # 401
            HttpStatusCode.FORBIDDEN,  # 403
            HttpStatusCode.NOT_FOUND,  # 404
        ]

        for status_code in non_retryable_status_codes:
            response = Response(status_code=status_code)
            request = Request("GET", "http://testserver")
            exception = HTTPStatusError(message="", request=request, response=response)
            assert ChaturbateUtils.need_retry(exception) is False

    def test_need_retry_with_non_http_exception(self) -> None:
        """Test need_retry function with non-HTTP exception."""
        exception = ValueError("Test error")
        assert ChaturbateUtils.need_retry(exception) is False
