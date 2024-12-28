import pytest
from httpx import AsyncClient, ConnectError


class TestHTTPClient:
    """Tests for HTTP client behavior."""

    @pytest.mark.asyncio
    async def test_request_success(self) -> None:
        """Test successful HTTP request."""
        async with AsyncClient() as client:
            response = await client.get("https://example.com")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_request_failure(self) -> None:
        """Test failure in HTTP request."""
        async with AsyncClient() as client:
            with pytest.raises(ConnectError):
                await client.get("https://nonexistent.url")
