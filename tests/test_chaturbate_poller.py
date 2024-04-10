"""Tests for the Chaturbate Poller module."""

import logging.config
import typing

import pytest
from chaturbate_poller.chaturbate_poller import ChaturbateClient, need_retry
from chaturbate_poller.format_messages import format_message, format_user_event
from chaturbate_poller.logging_config import LOGGING_CONFIG
from chaturbate_poller.models import (
    Event,
    EventData,
    EventsAPIResponse,
    Gender,
    Media,
    MediaType,
    Message,
    Tip,
    User,
)
from httpx import (
    AsyncClient,
    HTTPStatusError,
    Request,
    Response,
    TimeoutException,
)
from pytest_mock import MockerFixture

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


INVALID_TIP_EVENT_DATA = {
    "events": [
        {
            "method": "tip",
            "object": {
                "tip": {
                    "tokens": 0,
                    "isAnon": False,
                    "message": "Test message",
                },
                "user": {
                    "username": "fan_user",
                    "inFanclub": True,
                    "hasTokens": True,
                    "isMod": False,
                    "gender": "m",
                    "recentTips": "none",
                },
            },
            "id": "event_id_1",
        }
    ],
    "nextUrl": TEST_URL,
}


TEST_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
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


class TestTipModel:
    """Tests for the Tip model."""

    def test_validate_tokens_valid_value(self) -> None:
        """Test validate_tokens with a valid value."""
        valid_value = 10
        assert Tip(tokens=valid_value, isAnon=False, message="") == Tip(
            tokens=valid_value, isAnon=False, message=""
        )

    def test_validate_tokens_invalid_value(self) -> None:
        """Test validate_tokens with an invalid value."""
        invalid_value = 0
        with pytest.raises(ValueError, match="Tokens must be greater than 0."):
            Tip(tokens=invalid_value, isAnon=False, message="")
        with pytest.raises(ValueError, match="Tokens must be greater than 0."):
            Tip(tokens=-1, isAnon=False, message="")


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


class TestMessageFormatting:
    """Tests for message formatting."""

    @pytest.fixture()
    def example_user(self) -> User:
        """Return an example User object."""
        return User(
            username="example_user",
            inFanclub=False,
            gender=Gender.MALE,
            hasTokens=True,
            recentTips="none",
            isMod=False,
        )

    @pytest.fixture()
    def media_photos(self) -> Media:
        """Return an example Media object."""
        return Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)

    @pytest.fixture()
    def tip_example(self) -> Tip:
        """Return an example Tip object."""
        return Tip(tokens=100, message="example message", isAnon=False)

    @pytest.fixture()
    def message_example(self) -> Message:
        """Return an example Message object."""
        return Message(
            fromUser="example_user",
            message="example message",
            color="example_color",
            font="example_font",
            toUser="user",
            bgColor="example_bg_color",
        )

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        ("event_method", "event_data_func", "expected_message"),
        [
            (
                "mediaPurchase",
                lambda user, media, _: EventData(
                    broadcaster="example_broadcaster", user=user, media=media
                ),
                "example_user purchased photos set: photoset1",
            ),
            (
                "tip",
                lambda user, _, tip: EventData(
                    broadcaster="example_broadcaster", user=user, tip=tip
                ),
                "example_user tipped 100 tokens with message: 'example message'",
            ),
            (
                "roomSubjectChange",
                lambda _, __, ___: EventData(
                    broadcaster="example_broadcaster", subject="example subject"
                ),
                "Room Subject changed to example subject",
            ),
            (
                "chatMessage",
                lambda _, __, ___: EventData(
                    broadcaster="example_broadcaster",
                    message=Message(
                        fromUser="example_user",
                        message="example message",
                        color="red",
                        font="Arial",
                        toUser="user",
                        bgColor="white",
                    ),
                ),
                "example_user sent message: example message",
            ),
            (
                "fanclubJoin",
                lambda user, _, __: EventData(
                    broadcaster="example_broadcaster", user=user
                ),
                "example_user joined the fanclub",
            ),
            (
                "userEnter",
                lambda user, _, __: EventData(
                    broadcaster="example_broadcaster", user=user
                ),
                "example_user entered the room",
            ),
            (
                "userLeave",
                lambda user, _, __: EventData(
                    broadcaster="example_broadcaster", user=user
                ),
                "example_user left the room",
            ),
            (
                "follow",
                lambda user, _, __: EventData(
                    broadcaster="example_broadcaster", user=user
                ),
                "example_user followed",
            ),
            (
                "unfollow",
                lambda user, _, __: EventData(
                    broadcaster="example_broadcaster", user=user
                ),
                "example_user unfollowed",
            ),
        ],
    )
    async def test_events(  # noqa: PLR0913
        self,
        example_user: User,
        media_photos: Media,
        tip_example: Tip,
        event_method: str,
        event_data_func: typing.Callable,
        expected_message: str,
    ) -> None:
        """Test the formatting of various events."""
        event_data = event_data_func(example_user, media_photos, tip_example)
        event = Event(method=event_method, object=event_data, id="UNIQUE_EVENT_ID")
        formatted_message = await format_message(event)
        assert formatted_message == expected_message

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        ("tip_message", "is_anon", "expected_suffix"),
        [
            (
                "example message",
                False,
                "tipped 100 tokens with message: 'example message'",
            ),
            ("", False, "tipped 100 tokens "),
            (
                "example message",
                True,
                "tipped anonymously 100 tokens with message: 'example message'",
            ),
        ],
    )
    async def test_tip_variants(  # noqa: PLR0913
        self,
        example_user: User,
        tip_example: Tip,
        tip_message: str,
        is_anon: bool,  # noqa: FBT001
        expected_suffix: str,
    ) -> None:
        """Test the formatting of tip events."""
        tip_example.message = tip_message
        tip_example.is_anon = is_anon  # Adjusted to the correct property name
        event_data = EventData(
            broadcaster="example_broadcaster", user=example_user, tip=tip_example
        )
        event = Event(method="tip", object=event_data, id="UNIQUE_EVENT_ID")
        formatted_message = await format_message(event)
        assert formatted_message == f"example_user {expected_suffix}"

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        ("event_method", "expected_message"),
        [
            ("broadcastStart", "Broadcast started"),
            ("broadcastStop", "Broadcast stopped"),
            ("unknown", "Unknown method: unknown"),
            ("tip", "Unknown tip event"),
            ("chatMessage", "Unknown message event"),
            ("roomSubjectChange", "Room Subject changed to unknown"),
            ("mediaPurchase", "Unknown media purchase event"),
            ("fanclubJoin", "Unknown user joined the fanclub"),
            ("userEnter", "Unknown user entered the room"),
            ("userLeave", "Unknown user left the room"),
        ],
    )
    async def test_unknown_and_special_events(
        self,
        event_method: str,
        expected_message: str,
    ) -> None:
        """Test the formatting of unknown and special events."""
        event = Event(method=event_method, object=EventData(), id="UNIQUE_EVENT_ID")
        formatted_message = await format_message(event)
        assert formatted_message == expected_message

    def test_direct_unknown_user_event(self, example_user: User) -> None:
        """Test the formatting of unknown user events."""
        event_data = EventData(broadcaster="example_broadcaster", user=example_user)
        event = Event(method="unknown", object=event_data, id="UNIQUE_EVENT_ID")
        formatted_message = format_user_event(event)
        assert formatted_message == "Unknown user event"
