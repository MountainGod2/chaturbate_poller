import pytest
from httpx import AsyncClient

from chaturbate_poller.constants import API_TIMEOUT, TESTBED_BASE_URL
from chaturbate_poller.core.client import ChaturbateClient

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
            assert isinstance(client._client, AsyncClient)

    @pytest.mark.asyncio
    async def test_client_closed_correctly(self) -> None:
        """Test that the client is closed properly."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert client._client is not None
            await client.__aexit__(None, None, None)
        assert client._client is None

    @pytest.mark.parametrize(
        ("username", "token"),
        [("", TOKEN), (USERNAME, ""), ("", "")],
    )
    @pytest.mark.asyncio
    async def test_initialization_failure(self, username: str, token: str) -> None:
        """Test failure cases during initialization."""
        with pytest.raises(ValueError, match=r"Chaturbate username and token are required."):
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
        with pytest.raises(ValueError, match=r"Timeout must be a non-negative integer."):
            async with ChaturbateClient(USERNAME, TOKEN, timeout=-1):
                pass

    @pytest.mark.asyncio
    async def test_uninitialized_client(self) -> None:
        """Test that using an uninitialized client raises RuntimeError."""
        client = ChaturbateClient(USERNAME, TOKEN)
        with pytest.raises(
            RuntimeError,
            match=r"Client has not been initialized. Use 'async with ChaturbateClient\(\)'.",
        ):
            await client.fetch_events()
