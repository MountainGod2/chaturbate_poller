import logging
from typing import Any

import pytest
from httpx import (
    HTTPStatusError,
    Request,
    Response,
)

from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.utils import ChaturbateUtils


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

    def test_giveup_handler(self, caplog: Any) -> None:
        """Test the giveup handler."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match="Giving up due to unhandled polling error"):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item, typeddict-unknown-key]
                "tries": 6,
                "exception": HTTPStatusError(
                    message="Server Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(500, json={"status": "Unknown error"}),
                ),
            })
        assert "Giving up after 6 tries due to server error: Status code 500" in caplog.text

    @pytest.mark.parametrize(
        ("http_code", "error_message"),
        [
            (HttpStatusCode.FORBIDDEN, "Giving up due to invalid credentials"),
            (HttpStatusCode.NOT_FOUND, "Giving up due to invalid username"),
            (HttpStatusCode.UNAUTHORIZED, "Giving up due to invalid token"),
        ],
    )
    def test_giveup_handler_no_retry(self, caplog: Any, http_code: int, error_message: str) -> None:
        """Test the giveup handler with no retry."""
        caplog.set_level(logging.ERROR)
        with pytest.raises(PollingError, match=error_message):
            ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
                "tries": 1,
                "exception": HTTPStatusError(
                    message="Server Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(http_code, json={"status": "Unknown error"}),
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
