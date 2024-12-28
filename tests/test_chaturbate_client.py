import pytest
from httpx import AsyncClient

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.constants import API_TIMEOUT, TESTBED_BASE_URL

from .constants import TOKEN, USERNAME


class TestChaturbateClient:
    """Tests for ChaturbateClient."""

    @pytest.mark.asyncio
    async def test_initialization(self) -> None:
        """Test successful initialization of ChaturbateClient."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert client.username == USERNAME
            assert client.token == TOKEN

    @pytest.mark.asyncio
    async def test_initialization_with_custom_timeout(self) -> None:
        """Test initialization with a custom timeout."""
        timeout = API_TIMEOUT
        async with ChaturbateClient(USERNAME, TOKEN, timeout=timeout) as client:
            assert client.timeout == timeout

    @pytest.mark.asyncio
    async def test_initialization_with_testbed(self) -> None:
        """Test initialization with testbed base URL."""
        async with ChaturbateClient(USERNAME, TOKEN, testbed=True) as client:
            assert client.base_url == TESTBED_BASE_URL

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test client as a context manager."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert isinstance(client.client, AsyncClient)

    @pytest.mark.asyncio
    async def test_client_closed_correctly(self) -> None:
        """Test that the client is closed properly."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            await client.client.aclose()
        assert client.client.is_closed

    @pytest.mark.parametrize(
        ("username", "token"),
        [("", TOKEN), (USERNAME, ""), ("", "")],
    )
    @pytest.mark.asyncio
    async def test_initialization_failure(self, username: str, token: str) -> None:
        """Test failure cases during initialization."""
        with pytest.raises(ValueError, match="Chaturbate username and token are required."):
            async with ChaturbateClient(username, token):
                pass

    @pytest.mark.asyncio
    async def test_invalid_timeout(self) -> None:
        """Test initialization with invalid timeout."""
        with pytest.raises(TypeError):
            async with ChaturbateClient(USERNAME, TOKEN, timeout="invalid"):  # type: ignore  # noqa: PGH003
                pass

    @pytest.mark.asyncio
    async def test_negative_timeout(self) -> None:
        """Test initialization with a negative timeout."""
        with pytest.raises(ValueError, match="Timeout must be a positive integer."):
            async with ChaturbateClient(USERNAME, TOKEN, timeout=-1):
                pass
