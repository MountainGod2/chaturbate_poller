from chaturbate_poller.constants import HttpStatusCode

from .constants import TEST_URL, TOKEN, USERNAME


class TestConstants:
    """Tests for the constants."""

    def test_base_url(self) -> None:
        """Test the base URL."""
        assert f"https://eventsapi.chaturbate.com/events/{USERNAME}/{TOKEN}/" == TEST_URL

    def test_http_status_codes(self) -> None:
        """Test the HTTP status codes."""
        assert HttpStatusCode.OK == 200
        assert HttpStatusCode.CREATED == 201
        assert HttpStatusCode.ACCEPTED == 202
        assert HttpStatusCode.NO_CONTENT == 204
        assert HttpStatusCode.BAD_REQUEST == 400
        assert HttpStatusCode.UNAUTHORIZED == 401
        assert HttpStatusCode.FORBIDDEN == 403
        assert HttpStatusCode.NOT_FOUND == 404
        assert HttpStatusCode.METHOD_NOT_ALLOWED == 405
        assert HttpStatusCode.CONFLICT == 409
        assert HttpStatusCode.INTERNAL_SERVER_ERROR == 500
        assert HttpStatusCode.NOT_IMPLEMENTED == 501
        assert HttpStatusCode.BAD_GATEWAY == 502
        assert HttpStatusCode.SERVICE_UNAVAILABLE == 503
        assert HttpStatusCode.GATEWAY_TIMEOUT == 504
