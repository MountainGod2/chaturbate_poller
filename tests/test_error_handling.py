import pytest
from httpx import HTTPStatusError, Request, Response

from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.utils.error_handler import handle_giveup
from chaturbate_poller.utils.helpers import need_retry


class TestErrorHandling:
    """Tests for error handling utilities."""

    @pytest.mark.parametrize(
        ("exception", "expected_retry"),
        [
            (
                HTTPStatusError(
                    message="Server Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(500),
                ),
                True,
            ),
            (
                HTTPStatusError(
                    message="Client Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(400),
                ),
                False,
            ),
        ],
    )
    def test_need_retry(self, exception: HTTPStatusError, expected_retry: bool) -> None:
        """Test need_retry function with various HTTP errors."""
        result = need_retry(exception)
        assert result is expected_retry

    def test_giveup_handler(self) -> None:
        """Test giveup_handler raises PollingError with correct message."""
        tries = 6

        with pytest.raises(
            PollingError,
            match="Unhandled polling error encountered.",
        ):
            handle_giveup({
                "tries": tries,
                "target": lambda: None,
                "args": (),
                "kwargs": {},
                "elapsed": 0.0,
            })
