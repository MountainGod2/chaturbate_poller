from chaturbate_poller.constants import HttpStatusCode

from .constants import TEST_URL, TOKEN, USERNAME


class TestConstants:
    """Tests for constants."""

    def test_base_url(self) -> None:
        """Test the constructed base URL."""
        expected_url = f"https://eventsapi.chaturbate.com/events/{USERNAME}/{TOKEN}/"
        assert expected_url == TEST_URL

    def test_http_status_codes(self) -> None:
        """Test HTTP status codes."""
        assert HttpStatusCode.OK.value == 200
        assert HttpStatusCode.CREATED.value == 201
        assert HttpStatusCode.ACCEPTED.value == 202
        assert HttpStatusCode.NO_CONTENT.value == 204
        assert HttpStatusCode.BAD_REQUEST.value == 400
        assert HttpStatusCode.UNAUTHORIZED.value == 401
        assert HttpStatusCode.FORBIDDEN.value == 403
        assert HttpStatusCode.NOT_FOUND.value == 404
        assert HttpStatusCode.METHOD_NOT_ALLOWED.value == 405
        assert HttpStatusCode.CONFLICT.value == 409
        assert HttpStatusCode.INTERNAL_SERVER_ERROR.value == 500
        assert HttpStatusCode.NOT_IMPLEMENTED.value == 501
        assert HttpStatusCode.BAD_GATEWAY.value == 502
        assert HttpStatusCode.SERVICE_UNAVAILABLE.value == 503
        assert HttpStatusCode.GATEWAY_TIMEOUT.value == 504
