import asyncio

import pytest

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.constants import API_TIMEOUT, TESTBED_BASE_URL

from .constants import TOKEN, USERNAME


class TestChaturbateClientInitialization:
    """Tests for the initialization of ChaturbateClient."""

    @pytest.mark.asyncio
    async def test_initialization(self) -> None:
        """Test successful initialization of ChaturbateClient with default settings."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert client.username == USERNAME
            assert client.token == TOKEN

    @pytest.mark.asyncio
    async def test_initialization_with_timeout(self) -> None:
        """Test ChaturbateClient initialization with custom timeout."""
        timeout = API_TIMEOUT
        async with ChaturbateClient(USERNAME, TOKEN, timeout=timeout) as client:
            assert client.timeout == timeout

    @pytest.mark.asyncio
    async def test_initialization_with_testbed(self) -> None:
        """Test ChaturbateClient initialization with testbed base URL."""
        async with ChaturbateClient(USERNAME, TOKEN, testbed=True) as client:
            assert client.base_url == TESTBED_BASE_URL

    @pytest.mark.parametrize(("username", "token"), [("", TOKEN), (USERNAME, ""), ("", "")])
    @pytest.mark.asyncio
    async def test_initialization_failure(self, username: str, token: str) -> None:
        """Test ChaturbateClient initialization failure with missing username or token."""
        with pytest.raises(ValueError, match="Chaturbate username and token are required."):
            async with ChaturbateClient(username, token):
                await asyncio.sleep(0)

    @pytest.mark.asyncio
    async def test_initialization_with_invalid_timeout(self) -> None:
        """Test ChaturbateClient initialization with invalid timeout."""
        invalid_timeout = "invalid_timeout"
        with pytest.raises(TypeError):
            async with ChaturbateClient(USERNAME, TOKEN, timeout=invalid_timeout):  # type: ignore[arg-type]
                pass

    @pytest.mark.asyncio
    async def test_initialization_with_negative_timeout(self) -> None:
        """Test ChaturbateClient initialization with negative timeout."""
        negative_timeout = -1
        with pytest.raises(ValueError, match="Timeout must be a positive integer."):
            async with ChaturbateClient(USERNAME, TOKEN, timeout=negative_timeout):
                pass

    @pytest.mark.asyncio
    async def test_initialization_with_missing_env_variables(self) -> None:
        """Test ChaturbateClient initialization with missing environment variables."""
        with pytest.raises(ValueError, match="Chaturbate username and token are required."):
            async with ChaturbateClient("", ""):
                pass
