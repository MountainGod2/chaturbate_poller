import pytest
from httpx import HTTPStatusError, Request, Response

from chaturbate_poller.utils.helpers import ChaturbateUtils


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
    def test_need_retry(self, exception: Exception, expected_retry: bool) -> None:
        """Test whether retries are needed based on exceptions."""
        assert ChaturbateUtils().need_retry(exception) == expected_retry
