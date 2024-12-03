import logging
from typing import Any, TypedDict

import pytest
from httpx import (
    HTTPStatusError,
    Request,
    Response,
)

from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.utils import ChaturbateUtils


class Details(TypedDict, total=False):
    """Type definition for backoff handler details."""

    tries: int
    wait: float
    target: Any
    args: tuple
    kwargs: dict
    elapsed: float
    exception: HTTPStatusError


class TestBackoffHandlers:
    """Tests for the backoff handlers."""

    @pytest.mark.parametrize(
        ("wait", "tries", "expected_log"),
        [
            (1.0, 1, "Backing off 1 seconds after 1 tries"),
            (2.0, 3, "Backing off 2 seconds after 3 tries"),
        ],
    )
    def test_backoff_handler(self, caplog: Any, wait: float, tries: int, expected_log: str) -> None:
        """Test the backoff handler with different parameters."""
        caplog.set_level(logging.INFO)
        ChaturbateUtils().backoff_handler({
            "wait": wait,
            "tries": tries,
            "target": lambda x: x,
            "args": (),
            "kwargs": {},
            "elapsed": 0,
        })
        assert expected_log in caplog.text

    @pytest.mark.parametrize(
        ("status_code", "expected_message"),
        [
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
        ],
    )
    def test_giveup_handler_server_errors(
        self, caplog: Any, status_code: int, expected_message: str
    ) -> None:
        """Test giveup handler with different server error status codes."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match="Giving up due to unhandled polling error"):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 3,
                "exception": HTTPStatusError(
                    message="Server Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(status_code, json={"error": expected_message}),
                ),
            })
        assert (
            f"Giving up after 3 tries due to server error: Status code {status_code}" in caplog.text
        )

    def test_backoff_handler_with_kwargs(self, caplog: Any) -> None:
        """Test backoff handler with custom kwargs."""
        caplog.set_level(logging.INFO)
        test_kwargs = {"retry_count": 5}
        ChaturbateUtils().backoff_handler({
            "wait": 1.5,
            "tries": 2,
            "target": lambda x: x,
            "args": (),
            "kwargs": test_kwargs,
            "elapsed": 0.5,
        })
        assert "Backing off 1 seconds after 2 tries" in caplog.text

    def test_backoff_handler_with_target_function(self, caplog: Any) -> None:
        """Test backoff handler with a specific target function."""

        def test_func(x: int) -> int:
            return x * 2

        caplog.set_level(logging.INFO)
        ChaturbateUtils().backoff_handler({
            "wait": 1.0,
            "tries": 1,
            "target": test_func,
            "args": (5,),
            "kwargs": {},
            "elapsed": 0.1,
        })
        assert "Backing off 1 seconds after 1 tries" in caplog.text

    @pytest.mark.parametrize(
        ("http_code", "error_message", "expected_message"),
        [
            (400, "Client Error", "Giving up due to unhandled polling error"),
            (401, "Unauthorized", "Giving up due to invalid token"),
            (403, "Forbidden", "Giving up due to invalid credentials"),
            (404, "Not Found", "Giving up due to invalid username"),
        ],
    )
    def test_giveup_handler_no_retry(
        self, caplog: Any, http_code: int, error_message: str, expected_message: str
    ) -> None:
        """Test the giveup handler with no retry."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match=expected_message):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 1,
                "exception": HTTPStatusError(
                    message="Server Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(http_code, json={"error": error_message}),
                ),
            })
        assert (
            f"Giving up after 1 tries due to server error: Status code {http_code}" in caplog.text
        )

    def test_giveup_handler_no_exception(self, caplog: Any) -> None:
        """Test the giveup handler with no exception."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 6,
            })
        assert "Giving up after 6 tries due to server error: Status code None" in caplog.text
