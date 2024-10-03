import pytest
from httpx import (
    AsyncClient,
    ConnectError,
)


class TestHTTPClient:
    """Tests for the HTTP client."""

    @pytest.mark.asyncio
    async def test_http_client_request_success(self) -> None:
        """Test HTTP client request success."""
        async with AsyncClient() as client:
            response = await client.get("https://example.com")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_http_client_request_failure(self) -> None:
        """Test HTTP client request failure."""
        async with AsyncClient() as client:
            with pytest.raises(ConnectError):
                await client.get("https://nonexistent.url")
