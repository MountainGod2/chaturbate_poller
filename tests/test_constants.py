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
        assert HttpStatusCode.NO_CONTENT.value == 204
        assert HttpStatusCode.BAD_REQUEST.value == 400
        assert HttpStatusCode.UNAUTHORIZED.value == 401
        assert HttpStatusCode.FORBIDDEN.value == 403
        assert HttpStatusCode.NOT_FOUND.value == 404
        assert HttpStatusCode.INTERNAL_SERVER_ERROR.value == 500
        assert HttpStatusCode.BAD_GATEWAY.value == 502
        assert HttpStatusCode.SERVICE_UNAVAILABLE.value == 503
        assert HttpStatusCode.GATEWAY_TIMEOUT.value == 504
        assert HttpStatusCode.CLOUDFLARE_ERROR.value == 520
        assert HttpStatusCode.WEB_SERVER_IS_DOWN.value == 521
