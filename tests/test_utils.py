import logging
from typing import Any

import pytest
from httpx import HTTPStatusError, Request, Response

from chaturbate_poller.constants import MAX_RETRIES, HttpStatusCode
from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.utils import helpers
from chaturbate_poller.utils.error_handler import handle_giveup, log_backoff


class TestUtils:
    """Tests for the utility functions."""

    def _create_http_error(self, status_code: int, message: str = "Test Error") -> HTTPStatusError:
        """Helper method to create HTTPStatusError instances."""
        return HTTPStatusError(
            message=message,
            request=Request("GET", "https://error.url.com"),
            response=Response(status_code),
        )

    def test_get_max_tries(self) -> None:
        """Test get_max_tries returns the correct MAX_RETRIES value."""
        result = helpers.get_max_tries()
        assert result == MAX_RETRIES
        assert result == 6

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
        log_backoff({
            "wait": wait,
            "tries": tries,
            "target": lambda: None,
            "elapsed": 0,
            "args": (),
            "kwargs": {},
        })
        assert expected_log in caplog.text

    @pytest.mark.parametrize(
        ("status_code", "expected_message"),
        [
            (400, "Unhandled polling error encountered."),
            (401, "Invalid token or unauthorized access."),
            (403, "Access forbidden. Check credentials."),
            (404, "Resource not found."),
            (500, "Unhandled polling error encountered."),
            (502, "Unhandled polling error encountered."),
            (503, "Unhandled polling error encountered."),
            (504, "Unhandled polling error encountered."),
        ],
    )
    def test_giveup_handler_status_codes(
        self, caplog: Any, status_code: int, expected_message: str
    ) -> None:
        """Test giveup handler with various HTTP status codes."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match=expected_message):
            handle_giveup({  # type: ignore[typeddict-item]
                "tries": 3,
                "exception": self._create_http_error(status_code, "Test Error"),
            })

        # Verify error was logged
        assert f"Status code: {status_code}" in caplog.text

    def test_giveup_handler_no_exception(self, caplog: Any) -> None:
        """Test giveup handler when no exception is present."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match="Unhandled polling error encountered."):
            handle_giveup({  # type: ignore[typeddict-item]
                "tries": 6,
                "exception": self._create_http_error(500, "Unknown Error"),
            })

        # Verify logging occurred
        assert "Giving up after 6 tries" in caplog.text
        assert "Status code: 500" in caplog.text

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
            assert helpers.need_retry(exception) is True

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
            assert helpers.need_retry(exception) is False

    def test_need_retry_with_non_http_exception(self) -> None:
        """Test need_retry function with non-HTTP exception."""
        exception = ValueError("Test error")
        assert helpers.need_retry(exception) is False
