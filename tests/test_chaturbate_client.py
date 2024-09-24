# ruff: noqa: PLR0913, RUF100, S101
"""Tests for the Chaturbate poller."""

import asyncio
import logging.config
import typing

import pytest
from httpx import (
    AsyncClient,
    ConnectError,
    HTTPStatusError,
    ReadTimeout,
    Request,
    Response,
    TimeoutException,
)
from pydantic import ValidationError
from pytest_mock import MockerFixture

from chaturbate_poller.chaturbate_client import (
    ChaturbateClient,
    backoff_handler,
    giveup_handler,
    need_retry,
)
from chaturbate_poller.constants import API_TIMEOUT, TESTBED_BASE_URL, HttpStatusCode
from chaturbate_poller.format_messages import format_message, format_user_event
from chaturbate_poller.logging_config import LOGGING_CONFIG, CustomFormatter
from chaturbate_poller.models import (
    Event,
    EventData,
    Gender,
    Media,
    MediaType,
    Message,
    Tip,
    User,
)

USERNAME = "testuser"
"""str: The Chaturbate username."""
TOKEN = "testtoken"  # noqa: S105
"""str: The Chaturbate token."""
TEST_URL = "https://eventsapi.chaturbate.com/events/testuser/testtoken/"
"""str: The test URL for fetching Chaturbate events."""
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
"""dict: The test event data."""

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
"""dict: The test event data with an invalid tip event."""

TEST_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "()": CustomFormatter,
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(message)s",  # noqa: E501
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "tests.log",
            "formatter": "detailed",
            "level": "DEBUG",
            "backupCount": 0,
            "maxBytes": 0,
            "mode": "w",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "chaturbate_poller": {
            "level": "INFO",
        },
        "httpx": {
            "level": "WARNING",
        },
        "backoff": {
            "level": "WARNING",
        },
        "asyncio": {
            "level": "WARNING",
        },
        "httpcore": {
            "level": "WARNING",
        },
    },
}

"""dict: The test logging configuration."""


@pytest.fixture(autouse=True)
def _setup_logging() -> None:
    logging.config.dictConfig(TEST_LOGGING_CONFIG)
    logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture
def http_client_mock(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking the httpx.AsyncClient.get method.

    Args:
        mocker (MockerFixture): The mocker fixture.

    Returns:
        MockerFixture: The mocker fixture.
    """
    return mocker.patch("httpx.AsyncClient.get")


@pytest.fixture
def chaturbate_client() -> ChaturbateClient:
    """Fixture for creating a ChaturbateClient instance.

    Returns:
        ChaturbateClient: The ChaturbateClient instance.
    """
    return ChaturbateClient(USERNAME, TOKEN)


class TestBackoffHandlers:
    """Tests for the backoff handlers."""

    def test_backoff_handler(self, caplog) -> None:  # noqa: ANN001
        """Test the backoff handler."""
        caplog.set_level(logging.INFO)
        # Providing required keys "wait" and "tries" in the details dict
        backoff_handler(
            {
                "wait": 1.0,
                "tries": 1,
                "target": lambda x: x,
                "args": (),
                "kwargs": {},
                "elapsed": 0,
            }
        )
        assert "Backing off 1 seconds after 1 tries" in caplog.text

    def test_giveup_handler(self, caplog) -> None:  # noqa: ANN001
        """Test the giveup handler."""
        caplog.set_level(logging.ERROR)
        giveup_handler(
            {  # type: ignore[typeddict-item]
                "tries": 6,
                "exception": HTTPStatusError(
                    message="Server Error",
                    request=Request("GET", "https://error.url.com"),
                    response=Response(500, json={"status": "Unknown error"}),
                ),
            }
        )
        assert "Giving up after 6 tries due to server error code 500: Unknown error" in caplog.text

    def test_giveup_handler_no_exception(self, caplog) -> None:  # noqa: ANN001
        """Test the giveup handler with no exception."""
        caplog.set_level(logging.ERROR)
        giveup_handler(
            {  # type: ignore[typeddict-item]
                "tries": 6,
            }
        )
        assert (
            "Giving up after 6 tries due to server error code None: No response available"
            in caplog.text
        )


class TestConstants:
    """Tests for the constants."""

    def test_base_url(self) -> None:
        """Test the base URL."""
        assert TEST_URL == "https://eventsapi.chaturbate.com/events/testuser/testtoken/"

    def test_http_status_codes(self) -> None:
        """Test the HTTP status codes."""
        assert HttpStatusCode.OK == 200  # noqa: PLR2004
        assert HttpStatusCode.CREATED == 201  # noqa: PLR2004
        assert HttpStatusCode.ACCEPTED == 202  # noqa: PLR2004
        assert HttpStatusCode.NO_CONTENT == 204  # noqa: PLR2004
        assert HttpStatusCode.BAD_REQUEST == 400  # noqa: PLR2004
        assert HttpStatusCode.UNAUTHORIZED == 401  # noqa: PLR2004
        assert HttpStatusCode.FORBIDDEN == 403  # noqa: PLR2004
        assert HttpStatusCode.NOT_FOUND == 404  # noqa: PLR2004
        assert HttpStatusCode.METHOD_NOT_ALLOWED == 405  # noqa: PLR2004
        assert HttpStatusCode.CONFLICT == 409  # noqa: PLR2004
        assert HttpStatusCode.INTERNAL_SERVER_ERROR == 500  # noqa: PLR2004
        assert HttpStatusCode.NOT_IMPLEMENTED == 501  # noqa: PLR2004
        assert HttpStatusCode.BAD_GATEWAY == 502  # noqa: PLR2004
        assert HttpStatusCode.SERVICE_UNAVAILABLE == 503  # noqa: PLR2004
        assert HttpStatusCode.GATEWAY_TIMEOUT == 504  # noqa: PLR2004


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

        formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

    @pytest.mark.asyncio
    async def test_client_as_context_manager(self) -> None:
        """Test client as a context manager."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert isinstance(
                client.client, AsyncClient
            ), "Client should be an instance of AsyncClient during context management."

    @pytest.mark.asyncio
    async def test_client_closed_correctly(self, chaturbate_client: ChaturbateClient) -> None:
        """Test client is closed correctly."""
        async with chaturbate_client:
            await chaturbate_client.client.aclose()
        assert (
            chaturbate_client.client.is_closed
        ), "Client should be closed after exiting context manager."


class TestMiscellaneous:
    """Miscellaneous tests."""

    @pytest.mark.asyncio
    async def test_chaturbate_client_initialization(self) -> None:
        """Test ChaturbateClient initialization."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert client.username == USERNAME
            assert client.token == TOKEN

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_fetch_events_influxdb_error(self, mocker, chaturbate_client) -> None:  # noqa: ANN001
        """Test fetch_events method when InfluxDB write fails."""
        mocker.patch.object(
            chaturbate_client.influxdb_handler,
            "write_event",
            side_effect=Exception("InfluxDB Error"),
        )
        with pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."):
            await chaturbate_client.fetch_events()

    @pytest.mark.asyncio
    async def test_fetch_events_timeout(self, mocker, chaturbate_client) -> None:  # noqa: ANN001
        """Test fetch_events method when a timeout occurs."""
        mocker.patch.object(
            chaturbate_client.client, "get", side_effect=ReadTimeout("Request timed out")
        )

        with pytest.raises(ReadTimeout):
            await chaturbate_client.fetch_events()

    @pytest.mark.asyncio
    async def test_fetch_events_unhandled_exception(self, mocker) -> None:  # noqa: ANN001
        """Test fetch_events method handles unhandled exceptions properly."""
        mocker.patch("httpx.AsyncClient.get", side_effect=Exception("Unhandled error"))

        with pytest.raises(Exception, match="Unhandled error"):
            async with ChaturbateClient("test_user", "test_token") as client:
                await client.fetch_events()


class TestURLConstruction:
    """Tests for URL construction."""

    @pytest.mark.asyncio
    async def test_url_construction(self, chaturbate_client: ChaturbateClient) -> None:
        """Test URL construction."""
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == TEST_URL, "URL should be correctly constructed."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout(self, chaturbate_client: ChaturbateClient) -> None:
        """Test URL construction with timeout."""
        chaturbate_client.timeout = 10
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == f"{TEST_URL}?timeout=10", "URL should be correctly constructed with timeout."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout_zero(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout zero."""
        chaturbate_client.timeout = 0
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == TEST_URL, "URL should be correctly constructed without timeout."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout_none(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout None."""
        chaturbate_client.timeout = None
        url = chaturbate_client._construct_url()  # noqa: SLF001
        assert url == TEST_URL, "URL should be correctly constructed without timeout."


class TestMessageFormatting:
    """Tests for message formatting."""

    @pytest.fixture
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

    @pytest.fixture
    def media_photos(self) -> Media:
        """Return an example Media object."""
        return Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)

    @pytest.fixture
    def tip_example(self) -> Tip:
        """Return an example Tip object."""
        return Tip(tokens=100, message="example message", isAnon=False)

    @pytest.fixture
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

    @pytest.mark.asyncio
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
                lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
                "example_user joined the fanclub",
            ),
            (
                "userEnter",
                lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
                "example_user entered the room",
            ),
            (
                "userLeave",
                lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
                "example_user left the room",
            ),
            (
                "follow",
                lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
                "example_user followed",
            ),
            (
                "unfollow",
                lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
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

    @pytest.mark.asyncio
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
    async def test_tip_variants(
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

    @pytest.mark.asyncio
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


class TestModels:
    """Tests for the models."""

    def test_user_model(self) -> None:
        """Test the User model."""
        user = User(
            username="example_user",
            inFanclub=False,
            gender=Gender.MALE,
            hasTokens=True,
            recentTips="none",
            isMod=False,
        )
        assert user.username == "example_user"
        assert user.in_fanclub is False
        assert user.gender == Gender.MALE
        assert user.has_tokens is True
        assert user.recent_tips == "none"
        assert user.is_mod is False

    def test_message_model(self) -> None:
        """Test the Message model."""
        message = Message(
            fromUser="example_user",
            message="example message",
            color="example_color",
            font="example_font",
            toUser="user",
            bgColor="example_bg_color",
        )
        assert message.from_user == "example_user"
        assert message.message == "example message"
        assert message.color == "example_color"
        assert message.font == "example_font"
        assert message.to_user == "user"
        assert message.bg_color == "example_bg_color"

    def test_event_data_model(self) -> None:
        """Test the EventData model."""
        event_data = EventData(
            broadcaster="example_broadcaster",
            user=User(
                username="example_user",
                inFanclub=False,
                gender=Gender.MALE,
                hasTokens=True,
                recentTips="none",
                isMod=False,
            ),
            tip=Tip(
                tokens=100,
                message="example message",
                isAnon=False,
            ),
            media=Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25),
            subject="example subject",
            message=Message(
                fromUser="example_user",
                message="example message",
                color="example_color",
                font="example_font",
                toUser="user",
                bgColor="example_bg_color",
            ),
        )
        assert event_data.broadcaster == "example_broadcaster"
        if event_data.user is not None:
            assert event_data.user.username == "example_user"
            assert event_data.user.in_fanclub is False

        if event_data.tip is not None:
            assert event_data.tip.tokens == 100  # noqa: PLR2004
            assert event_data.tip.message == "example message"
            assert event_data.tip.is_anon is False

        if event_data.media is not None:
            assert event_data.media.id == 1
            assert event_data.media.name == "photoset1"
            assert event_data.media.type == MediaType.PHOTOS
            assert event_data.media.tokens == 25  # noqa: PLR2004

        if event_data.message is not None:
            assert event_data.message.from_user == "example_user"
            assert event_data.message.message == "example message"
            assert event_data.message.color == "example_color"
            assert event_data.message.font == "example_font"
            assert event_data.message.to_user == "user"
            assert event_data.message.bg_color == "example_bg_color"

        assert event_data.subject == "example subject"

    def test_event_model(self) -> None:
        """Test the Event model."""
        event = Event(
            method="userEnter",
            object=EventData(
                broadcaster="example_broadcaster",
                user=User(
                    username="example_user",
                    inFanclub=False,
                    gender=Gender.MALE,
                    hasTokens=True,
                    recentTips="none",
                    isMod=False,
                ),
            ),
            id="UNIQUE_EVENT_ID",
        )
        assert event.method == "userEnter"
        assert event.object.broadcaster == "example_broadcaster"
        if event.object.user is not None:
            assert event.object.user.username == "example_user"
        assert event.id == "UNIQUE_EVENT_ID"

    def test_tip_model(self) -> None:
        """Test the Tip model."""
        tip = Tip(tokens=100, message="example message", isAnon=False)
        assert tip.tokens == 100  # noqa: PLR2004
        assert tip.message == "example message"
        assert tip.is_anon is False

    def test_media_model(self) -> None:
        """Test the Media model."""
        media = Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)
        assert media.id == 1
        assert media.name == "photoset1"
        assert media.type == MediaType.PHOTOS
        assert media.tokens == 25  # noqa: PLR2004

    def test_enum_gender(self) -> None:
        """Test the Gender enum."""
        assert Gender.MALE.value == "m"
        assert Gender.FEMALE.value == "f"
        assert Gender.TRANS.value == "t"
        assert Gender.COUPLE.value == "c"

    def test_enum_media_type(self) -> None:
        """Test the MediaType enum."""
        assert MediaType.PHOTOS.value == "photos"
        assert MediaType.VIDEOS.value == "videos"


class TestHTTPClient:
    """Tests for the HTTP client."""

    @pytest.mark.asyncio
    async def test_http_client_request_success(self) -> None:
        """Test HTTP client request success."""
        async with AsyncClient() as client:
            response = await client.get("https://example.com")
            assert response.status_code == 200  # noqa: PLR2004

    @pytest.mark.asyncio
    async def test_http_client_request_failure(self) -> None:
        """Test HTTP client request failure."""
        async with AsyncClient() as client:
            with pytest.raises(ConnectError):
                await client.get("https://nonexistent.url")


class TestFormatMessages:
    """Tests for message formatting."""

    @pytest.mark.asyncio
    async def test_format_message_tip_with_message(self) -> None:
        """Test formatting a tip with a message."""
        message = await format_message(
            Event(
                method="tip",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=User(
                        username="example_user",
                        inFanclub=False,
                        gender=Gender.MALE,
                        hasTokens=True,
                        recentTips="none",
                        isMod=False,
                    ),
                    tip=Tip(tokens=100, message="example message", isAnon=False),
                ),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "example_user tipped 100 tokens with message: 'example message'"

    @pytest.mark.asyncio
    async def test_format_message_tip_without_message(self) -> None:
        """Test formatting a tip without a message."""
        message = await format_message(
            Event(
                method="tip",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=User(
                        username="example_user",
                        inFanclub=False,
                        gender=Gender.MALE,
                        hasTokens=True,
                        recentTips="none",
                        isMod=False,
                    ),
                    tip=Tip(tokens=100, message="", isAnon=False),
                ),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "example_user tipped 100 tokens "


class TestEventFormatting:
    """Tests for event formatting."""

    @pytest.mark.asyncio
    async def test_format_event_tip_with_message(self) -> None:
        """Test formatting a tip event with a message."""
        formatted_event = await format_message(
            Event(
                method="tip",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=User(
                        username="example_user",
                        inFanclub=False,
                        gender=Gender.MALE,
                        hasTokens=True,
                        recentTips="none",
                        isMod=False,
                    ),
                    tip=Tip(tokens=100, message="example message", isAnon=False),
                ),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert formatted_event == ("example_user tipped 100 tokens with message: 'example message'")

    @pytest.mark.asyncio
    async def test_format_event_tip_without_message(self) -> None:
        """Test formatting a tip event without a message."""
        formatted_event = await format_message(
            Event(
                method="tip",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=User(
                        username="example_user",
                        inFanclub=False,
                        gender=Gender.MALE,
                        hasTokens=True,
                        recentTips="none",
                        isMod=False,
                    ),
                    tip=Tip(tokens=100, message="", isAnon=False),
                ),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert formatted_event == "example_user tipped 100 tokens "


class TestLogFormat:
    """Tests for the log format."""

    def test_format_log(self) -> None:
        """Test log format."""
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )
        formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        formatted = formatter.format(log_record)
        assert "Test message" in formatted


class TestEventFetching:
    """Tests for fetching events."""

    @pytest.mark.asyncio
    async def test_fetch_events_undefined_json(
        self,
        chaturbate_client: ChaturbateClient,
        http_client_mock,  # noqa: ANN001
    ) -> None:
        """Test fetching events with undefined JSON."""
        request = Request("GET", TEST_URL)

        response_content = b'{"not": "json", "nextUrl": "https://example.com"}'
        http_client_mock.return_value = Response(200, content=response_content, request=request)
        with pytest.raises(ValidationError, match="1 validation error for EventsAPIResponse"):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        http_client_mock,  # noqa: ANN001
        chaturbate_client: ChaturbateClient,
    ) -> None:
        """Test unauthorized access."""
        request = Request("GET", TEST_URL)
        http_client_mock.return_value = Response(
            401,
            content=b'{"not": "json", "nextUrl": "https://example.com"}',
            request=request,
        )
        with pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_http_status_error(
        self,
        http_client_mock,  # noqa: ANN001
        chaturbate_client: ChaturbateClient,
        caplog,  # noqa: ANN001
    ) -> None:
        """Test HTTP status error."""
        request = Request("GET", TEST_URL)
        http_client_mock.return_value = Response(500, request=request)
        await chaturbate_client.fetch_events(TEST_URL)
        assert "Giving up after 6 tries due to server error code 500" in caplog.text


class TestNeedRetry:
    """Tests for the need_retry function."""

    @pytest.mark.parametrize(
        ("status_code", "expected"),
        [
            (HttpStatusCode.INTERNAL_SERVER_ERROR, True),
            (HttpStatusCode.BAD_GATEWAY, True),
            (HttpStatusCode.SERVICE_UNAVAILABLE, True),
            (HttpStatusCode.GATEWAY_TIMEOUT, True),
            (HttpStatusCode.WEB_SERVER_IS_DOWN, True),
            (HttpStatusCode.BAD_REQUEST, False),
            (HttpStatusCode.UNAUTHORIZED, False),
            (HttpStatusCode.FORBIDDEN, False),
            (HttpStatusCode.NOT_FOUND, False),
        ],
    )
    def test_http_status_error(self, status_code: int, *, expected: bool) -> None:
        """Test need_retry with HTTPStatusError exceptions."""
        exception = HTTPStatusError(
            message="Error",
            request=Request("GET", "https://error.url.com"),
            response=Response(status_code),
        )
        assert need_retry(exception) == expected

    def test_non_http_status_error(self) -> None:
        """Test need_retry with a non-HTTPStatusError exception."""
        exception = TimeoutException("Timeout occurred")
        assert not need_retry(exception)
