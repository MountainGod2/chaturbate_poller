"""Tests for the Chaturbate Poller module."""

import logging.config

import pytest
from chaturbate_poller.chaturbate_poller import ChaturbateClient, need_retry
from chaturbate_poller.logging_config import LOGGING_CONFIG
from chaturbate_poller.models import EventsAPIResponse
from httpx import (
    AsyncClient,
    HTTPStatusError,
    Request,
    Response,
    TimeoutException,
)
from pytest_mock import MockerFixture

from .test_logging_config import TEST_LOGGING_CONFIG

USERNAME = "testuser"
TOKEN = "testtoken"  # noqa: S105
TEST_URL = "https://events.testbed.cb.dev/events/testuser/testtoken/"
EVENT_DATA = {
    "events": [
        {
            "method": "userEnter",
            "object": {
                "user": {
                    "username": "fan_user",
                    "inFanclub": True,
                    "hasTokens": True,
                    "isMod": False,
                    "gender": "m",
                    "recentTips": "none",
                }
            },
            "id": "event_id_1",
        }
    ],
    "nextUrl": TEST_URL,
}


@pytest.fixture(autouse=True)
def _setup_logging() -> None:
    logging.config.dictConfig(TEST_LOGGING_CONFIG)


@pytest.fixture()
def http_client_mock(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking the httpx.AsyncClient.get method.

    Args:
        mocker (MockerFixture): The mocker fixture.

    Returns:
        MockerFixture: The mocker fixture.
    """
    return mocker.patch("httpx.AsyncClient.get")


@pytest.fixture()
def chaturbate_client() -> ChaturbateClient:
    """Fixture for creating a ChaturbateClient instance.

    Returns:
        ChaturbateClient: The ChaturbateClient instance.
    """
    return ChaturbateClient(USERNAME, TOKEN)


class TestChaturbateClientInitialization:
    """Tests for the ChaturbateClient initialization."""

    def test_initialization(self) -> None:
        """Test ChaturbateClient initialization."""
        client = ChaturbateClient(USERNAME, TOKEN)
        assert client.username == USERNAME
        assert client.token == TOKEN

    def test_initialization_with_timeout(self) -> None:
        """Test ChaturbateClient initialization with timeout."""
        timeout = 10
        client = ChaturbateClient(USERNAME, TOKEN, timeout=timeout)
        assert client.timeout == timeout

    def test_initialization_failure(self) -> None:
        """Test ChaturbateClient initialization failure."""
        with pytest.raises(
            ValueError, match="Chaturbate username and token are required."
        ):
            ChaturbateClient("", TOKEN)
        with pytest.raises(
            ValueError, match="Chaturbate username and token are required."
        ):
            ChaturbateClient(USERNAME, "")


class TestErrorHandling:
    """Tests for error handling."""

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
    def test_need_retry(
        self,
        exception: Exception,
        expected_retry: bool,  # noqa: FBT001
    ) -> None:
        """Test need_retry function."""
        assert need_retry(exception) == expected_retry


class TestLoggingConfigurations:
    """Tests for logging configurations."""

    def test_module_logging_configuration(self) -> None:
        """Test module logging configuration."""
        assert isinstance(LOGGING_CONFIG, dict)
        assert LOGGING_CONFIG.get("version") == 1
        assert LOGGING_CONFIG.get("disable_existing_loggers") is False

    def test_detailed_formatter(self) -> None:
        """Test detailed formatter."""
        from chaturbate_poller.logging_config import CustomFormatter

        formatter = CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )
        formatted = formatter.format(log_record)
        assert "Test message" in formatted


class TestClientLifecycle:
    """Tests for the client lifecycle."""

    @pytest.mark.asyncio()
    async def test_client_as_context_manager(self) -> None:
        """Test client as a context manager."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert isinstance(
                client.client, AsyncClient
            ), "Client should be an instance of AsyncClient during context management."

    @pytest.mark.asyncio()
    async def test_client_closed_correctly(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test client is closed correctly."""
        async with chaturbate_client:
            pass
        assert (
            chaturbate_client.client.is_closed
        ), "Client should be closed after exiting context manager."


class TestMiscellaneous:
    """Miscellaneous tests."""

    def test_chaturbate_client_initialization(self) -> None:
        """Test ChaturbateClient initialization."""
        client = ChaturbateClient(USERNAME, TOKEN)
        assert client.username == USERNAME, "Username should be correctly initialized."
        assert client.token == TOKEN, "Token should be correctly initialized."

    @pytest.mark.asyncio()
    async def test_timeout_handling(
        self,
        http_client_mock,  # noqa: ANN001
        chaturbate_client: ChaturbateClient,
    ) -> None:
        """Test timeout handling."""
        http_client_mock.side_effect = TimeoutException(
            message="Timeout", request=Request("GET", TEST_URL)
        )
        with pytest.raises(TimeoutException):
            await chaturbate_client.fetch_events(TEST_URL)


class TestURLConstruction:
    """Tests for URL construction."""

    @pytest.mark.asyncio()
    async def test_url_construction(self, chaturbate_client: ChaturbateClient) -> None:
        """Test URL construction."""
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == TEST_URL, "URL should be correctly constructed."

    @pytest.mark.asyncio()
    async def test_url_construction_with_timeout(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout."""
        chaturbate_client.timeout = 10
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert (
            url == f"{TEST_URL}?timeout=10"
        ), "URL should be correctly constructed with timeout."

    @pytest.mark.asyncio()
    async def test_url_construction_with_timeout_zero(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout zero."""
        chaturbate_client.timeout = 0
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == TEST_URL, "URL should be correctly constructed without timeout."

    @pytest.mark.asyncio()
    async def test_url_construction_with_timeout_none(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout None."""
        chaturbate_client.timeout = None
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == TEST_URL, "URL should be correctly constructed without timeout."


class TestEventFetching:
    """Tests for fetching events."""

    # Test url construction with no url passed
    @pytest.mark.asyncio()
    async def test_fetch_events_no_url(
        self,
        http_client_mock,  # noqa: ANN001
        chaturbate_client: ChaturbateClient,
    ) -> None:
        """Test fetching events with no URL."""
        request = Request("GET", TEST_URL)
        http_client_mock.return_value = Response(200, json=EVENT_DATA, request=request)
        response = await chaturbate_client.fetch_events()
        assert isinstance(response, EventsAPIResponse)
        http_client_mock.assert_called_once_with(TEST_URL, timeout=None)

    @pytest.mark.asyncio()
    async def test_fetch_events_malformed_json(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetching events with malformed JSON."""
        request = Request("GET", TEST_URL)
        self.return_value = Response(200, content=b"{not: 'json'}", request=request)
        with pytest.raises(HTTPStatusError):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        ("status_code", "should_succeed"),
        [
            (200, True),
            (400, False),
            (500, False),
        ],
    )
    async def test_fetch_events_http_statuses(
        self,
        http_client_mock,  # noqa: ANN001
        status_code: int,
        should_succeed: bool,  # noqa: FBT001
        chaturbate_client: ChaturbateClient,
    ) -> None:
        """Test fetching events with different HTTP statuses."""
        request = Request("GET", TEST_URL)
        http_client_mock.return_value = Response(
            status_code, json=EVENT_DATA, request=request
        )
        if should_succeed:
            response = await chaturbate_client.fetch_events(TEST_URL)
            assert isinstance(response, EventsAPIResponse)
        else:
            with pytest.raises(HTTPStatusError):
                await chaturbate_client.fetch_events(TEST_URL)
