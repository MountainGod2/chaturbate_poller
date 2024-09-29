# ruff: noqa: ANN401, FBT001,PLR0913,SIM117, PLR2004
"""Tests for the chaturbate_poller module."""

import asyncio
import logging
import logging.config
import os
import signal
import sys
from collections.abc import Callable
from contextlib import suppress
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import mock
from unittest.mock import AsyncMock, patch

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
from influxdb_client.rest import ApiException
from pydantic import ValidationError
from pytest_mock import MockerFixture
from urllib3.exceptions import NameResolutionError

from chaturbate_poller.__main__ import start_polling
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.constants import API_TIMEOUT, TESTBED_BASE_URL, HttpStatusCode
from chaturbate_poller.event_handler import (
    DatabaseEventHandler,
    LoggingEventHandler,
    create_event_handler,
)
from chaturbate_poller.format_messages import (
    format_media_purchase_event,
    format_message,
    format_message_event,
    format_tip_event,
    format_user_event,
)
from chaturbate_poller.influxdb_client import InfluxDBHandler
from chaturbate_poller.logging_config import (
    LOGGING_CONFIG,
    CustomFormatter,
    SanitizeURLFilter,
    sanitize_url,
)
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
from chaturbate_poller.signal_handler import SignalHandler
from chaturbate_poller.utils import ChaturbateUtils

USERNAME = "testuser"
TOKEN = "testtoken"  # noqa: S105
TEST_URL = f"https://eventsapi.chaturbate.com/events/{USERNAME}/{TOKEN}/"
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


@pytest.fixture(autouse=True)
def setup_logging() -> None:
    """Setup logging for tests."""
    logging.config.dictConfig(TEST_LOGGING_CONFIG)
    logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture
def http_client_mock(mocker: MockerFixture) -> Any:
    """Fixture for mocking the httpx.AsyncClient.get method."""
    return mocker.patch("httpx.AsyncClient.get")


@pytest.fixture
def chaturbate_client() -> ChaturbateClient:
    """Fixture for creating a ChaturbateClient instance."""
    return ChaturbateClient(USERNAME, TOKEN)


@pytest.fixture
def mock_influxdb_handler(mocker: Any) -> Any:
    """Fixture for the InfluxDB handler."""
    return mocker.Mock()


@pytest.fixture
def sample_event() -> Event:
    """Fixture for a sample event."""
    return Event(
        method="tip",
        object=EventData(
            user=User(
                username="test_user",
                inFanclub=False,
                hasTokens=True,
                isMod=False,
                recentTips="lots",
                gender=Gender("m"),
            ),
            tip=Tip(
                tokens=100,
                message="test message",
                isAnon=False,
            ),
        ),
        id="1",
    )


@pytest.fixture
def example_user() -> User:
    """Fixture for an example User object."""
    return User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )


@pytest.fixture
def media_photos() -> Media:
    """Fixture for an example Media object."""
    return Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)


@pytest.fixture
def tip_example() -> Tip:
    """Fixture for an example Tip object."""
    return Tip(tokens=100, message="example message", isAnon=False)


@pytest.fixture
def message_example() -> Message:
    """Fixture for an example Message object."""
    return Message(
        fromUser="example_user",
        message="example message",
        color="example_color",
        font="example_font",
        toUser="user",
        bgColor="example_bg_color",
    )


@pytest.fixture
def stop_future(event_loop: asyncio.AbstractEventLoop) -> asyncio.Future[None]:
    """Fixture for a future to set when the signal is received."""
    return event_loop.create_future()


@pytest.fixture
def signal_handler(
    event_loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]
) -> SignalHandler:
    """Fixture for an instance of the SignalHandler class."""
    return SignalHandler(event_loop, stop_future)


@pytest.fixture(scope="module")
def influxdb_handler() -> InfluxDBHandler:
    """Fixture for InfluxDBHandler."""
    return InfluxDBHandler()


class TestEnum(Enum):
    """Example enum for testing."""

    __test__ = False
    EXAMPLE = "example_value"


class TestInfluxDBClient:
    """Tests for the InfluxDBClient class."""

    def test_flatten_dict(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flatten_dict method."""
        nested_dict = {"level1": {"level2": "value", "level2b": {"level3": "value3"}}}
        flattened_dict = influxdb_handler.flatten_dict(nested_dict)
        expected_dict = {"level1.level2": "value", "level1.level2b.level3": "value3"}
        assert flattened_dict == expected_dict

    def test_flatten_dict_with_enum(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flatten_dict method with an enum value."""
        nested_dict = {"level1": {"enum_field": TestEnum.EXAMPLE, "other_field": "value"}}
        flattened_dict = influxdb_handler.flatten_dict(nested_dict)
        expected_dict = {"level1.enum_field": "example_value", "level1.other_field": "value"}
        assert flattened_dict == expected_dict

    @pytest.mark.parametrize(
        ("input_dict", "expected_dict"),
        [
            (
                {"key": "value", "nested": {"subkey": "subvalue"}},
                {"key": "value", "nested.subkey": "subvalue"},
            ),
            (
                {
                    "key": "value",
                    "nested": {"subkey": "subvalue", "subkey2": {"subsubkey": "value"}},
                },
                {"key": "value", "nested.subkey": "subvalue", "nested.subkey2.subsubkey": "value"},
            ),
        ],
    )
    def test_flatten_dict_with_params(
        self, influxdb_handler: InfluxDBHandler, input_dict: dict, expected_dict: dict
    ) -> None:
        """Test flatten_dict method with different parameters."""
        assert influxdb_handler.flatten_dict(input_dict) == expected_dict

    def test_write_event_success(self, influxdb_handler: InfluxDBHandler, mocker: Any) -> None:
        """Test write_event method success."""
        mock_write_api = mocker.patch.object(influxdb_handler.write_api, "write", autospec=True)
        event_data = {"event": "data"}
        influxdb_handler.write_event("test_measurement", event_data)
        mock_write_api.assert_called_once()

    def test_write_event_failure(
        self, influxdb_handler: InfluxDBHandler, mocker: Any, caplog: Any
    ) -> None:
        """Test write_event method when write fails."""
        mocker.patch.object(influxdb_handler.write_api, "write", side_effect=ApiException)
        event_data = {"event": "data"}

        with caplog.at_level(logging.ERROR), pytest.raises(ApiException):
            influxdb_handler.write_event("test_measurement", event_data)

        assert "Failed to write data to InfluxDB" in caplog.text

    def test_name_resolution_error(
        self, influxdb_handler: InfluxDBHandler, mocker: Any, caplog: Any
    ) -> None:
        """Test write_event method when name resolution fails."""
        mocker.patch.object(
            influxdb_handler.write_api,
            "write",
            side_effect=NameResolutionError(host="influxdb", conn=None, reason=None),  # type: ignore[arg-type]
        )
        event_data = {"event": "data"}

        with caplog.at_level(logging.ERROR), pytest.raises(NameResolutionError):
            influxdb_handler.write_event("test_measurement", event_data)

        assert "Failed to resolve InfluxDB URL" in caplog.text

    def test_close_handler(self, influxdb_handler: InfluxDBHandler, mocker: Any) -> None:
        """Test close method."""
        mock_close = mocker.patch.object(influxdb_handler.client, "close", autospec=True)
        influxdb_handler.close()
        mock_close.assert_called_once()

    def test_influxdb_handler_init(self) -> None:
        """Test InfluxDBHandler initialization."""
        with mock.patch.dict(
            os.environ, {"INFLUXDB_URL": "http://localhost:8086", "INFLUXDB_TOKEN": "test_token"}
        ):
            handler = InfluxDBHandler()
            assert handler.client.url == "http://localhost:8086"
            assert handler.client.token == "test_token"  # noqa: S105


class TestSignalHandler:
    """Tests for the signal handler."""

    def test_signal_handler_initialization(
        self,
        signal_handler: SignalHandler,
        event_loop: asyncio.AbstractEventLoop,
        stop_future: asyncio.Future[None],
    ) -> None:
        """Test the initialization of the SignalHandler class."""
        assert isinstance(signal_handler.logger, logging.Logger)
        assert signal_handler.loop is event_loop
        assert signal_handler.stop_future is stop_future

    def test_signal_handler_setup_non_windows(
        self, signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        """Test the setup method of the SignalHandler class on non-Windows platforms."""
        with mock.patch.object(sys, "platform", "linux"):
            with mock.patch.object(event_loop, "add_signal_handler") as mock_add_signal_handler:
                with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
                    signal_handler.setup()
                    mock_add_signal_handler.assert_any_call(
                        signal.SIGINT, signal_handler.handle_signal, signal.SIGINT
                    )
                    mock_add_signal_handler.assert_any_call(
                        signal.SIGTERM, signal_handler.handle_signal, signal.SIGTERM
                    )
                    mock_logger_debug.assert_called_with(
                        "Signal handlers set up for SIGINT and SIGTERM."
                    )

    def test_signal_handler_setup_windows(
        self, signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        """Test the setup method of the SignalHandler class on Windows platforms."""
        with mock.patch.object(sys, "platform", "win32"):
            with mock.patch.object(signal_handler.logger, "warning") as mock_logger_warning:
                signal_handler.setup()
                mock_logger_warning.assert_called_once_with(
                    "Signal handlers not supported on this platform."
                )
                with mock.patch.object(event_loop, "add_signal_handler") as mock_add_signal_handler:
                    mock_add_signal_handler.assert_not_called()

    def test_handle_signal(self, signal_handler: SignalHandler) -> None:
        """Test the handle_signal method of the SignalHandler class."""
        with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:
            with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
                signal_handler.handle_signal(signal.SIGINT)
                mock_create_task.assert_called_once()
                mock_logger_debug.assert_called_with(
                    "Received signal %s. Initiating shutdown.", signal.SIGINT.name
                )

    def test_handle_signal_various_signals(self, signal_handler: SignalHandler) -> None:
        """Test handle_signal with different signals."""
        with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:
            signal_handler.handle_signal(signal.SIGINT)
            mock_create_task.assert_called_once()
            mock_create_task.reset_mock()

            signal_handler.handle_signal(signal.SIGTERM)
            mock_create_task.assert_called_once()

    def test_handle_signal_future_done(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None]
    ) -> None:
        """Test handle_signal when the stop_future is already done."""
        stop_future.set_result(None)

        with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:
            signal_handler.handle_signal(signal.SIGINT)
            mock_create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown(self, signal_handler: SignalHandler) -> None:
        """Test the _shutdown method of the SignalHandler class."""
        with mock.patch.object(signal_handler, "_cancel_tasks") as mock_cancel_tasks:
            with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
                await signal_handler._shutdown()  # type: ignore[func-returns-value]
                assert signal_handler.stop_future.done()
                mock_cancel_tasks.assert_called_once()
                mock_logger_debug.assert_any_call("Shutting down tasks and cleaning up.")

    @pytest.mark.asyncio
    async def test_cancel_tasks(self, signal_handler: SignalHandler) -> None:
        """Test the _cancel_tasks method of the SignalHandler class."""
        current_task = asyncio.current_task()
        tasks = [asyncio.create_task(asyncio.sleep(1)) for _ in range(3)]
        await asyncio.sleep(0)

        with mock.patch("asyncio.all_tasks", return_value=[*tasks, current_task]):
            with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
                await signal_handler._cancel_tasks()
                for task in tasks:
                    assert task.cancelled()

                mock_logger_debug.assert_called_with("All tasks cancelled and cleaned up.")

    def test_shutdown_logging(self, signal_handler: SignalHandler) -> None:
        """Test logging during the _shutdown method."""
        with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
            with mock.patch.object(signal_handler, "_cancel_tasks"):
                asyncio.run(signal_handler._shutdown())
                mock_logger_debug.assert_any_call("Shutting down tasks and cleaning up.")


class TestBackoffHandlers:
    """Tests for the backoff handlers."""

    def test_backoff_handler(self, caplog: Any) -> None:
        """Test the backoff handler."""
        caplog.set_level(logging.INFO)
        ChaturbateUtils().backoff_handler({
            "wait": 1.0,
            "tries": 1,
            "target": lambda x: x,
            "args": (),
            "kwargs": {},
            "elapsed": 0,
        })
        assert "Backing off 1 seconds after 1 tries" in caplog.text

    def test_giveup_handler(self, caplog: Any) -> None:
        """Test the giveup handler."""
        caplog.set_level(logging.ERROR)
        ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item, typeddict-unknown-key]
            "tries": 6,
            "exception": HTTPStatusError(
                message="Server Error",
                request=Request("GET", "https://error.url.com"),
                response=Response(500, json={"status": "Unknown error"}),
            ),
        })
        assert "Giving up after 6 tries due to server error code 500: Unknown error" in caplog.text

    def test_giveup_handler_no_exception(self, caplog: Any) -> None:
        """Test the giveup handler with no exception."""
        caplog.set_level(logging.ERROR)
        ChaturbateUtils().giveup_handler({  # type: ignore[typeddict-item]
            "tries": 6,
        })
        assert (
            "Giving up after 6 tries due to server error code None: No response available"
            in caplog.text
        )


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


class TestEventHandler:
    """Tests for event handling."""

    def test_create_event_handler_logging(self) -> None:
        """Test the create_event_handler function with the logging handler."""
        handler = create_event_handler("logging")
        assert isinstance(handler, LoggingEventHandler)

    def test_create_event_handler_database(self) -> None:
        """Test the create_event_handler function with the database handler."""
        handler = create_event_handler("database")
        assert isinstance(handler, DatabaseEventHandler)

    @pytest.mark.asyncio
    async def test_logging_event_handler(self, sample_event: Event, caplog: Any) -> None:
        """Test the LoggingEventHandler."""
        handler = LoggingEventHandler()
        await handler.handle_event(sample_event)
        assert "test_user tipped 100 tokens with message: 'test message'" in caplog.text

    @pytest.mark.asyncio
    async def test_database_event_handler(
        self, mock_influxdb_handler: Any, sample_event: Event
    ) -> None:
        """Test the DatabaseEventHandler."""
        handler = DatabaseEventHandler(mock_influxdb_handler)
        await handler.handle_event(sample_event)
        mock_influxdb_handler.write_event.assert_called_once_with(
            "chaturbate_events", sample_event.model_dump()
        )

    @pytest.mark.asyncio
    async def test_create_event_handler_unknown(self) -> None:
        """Test the create_event_handler function with an unknown handler."""
        with pytest.raises(ValueError, match="Unknown handler type: unknown"):
            create_event_handler("unknown")


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
        expected_retry: bool,
    ) -> None:
        """Test need_retry function."""
        assert ChaturbateUtils().need_retry(exception) == expected_retry


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


class TestConfigManager:
    """Tests for the config module."""

    def test_load_config_from_file(self) -> None:
        """Test loading configuration from a YAML file."""
        with patch("os.getenv", side_effect=lambda _, d=None: d):
            with TemporaryDirectory() as tempdir:
                config_path = Path(tempdir) / "config.yaml"
                config_path.write_text(
                    """
                CB_USERNAME: "file_user"
                CB_TOKEN: "file_token"
                """,
                    encoding="utf-8",
                )

                config_manager = ConfigManager(config_file=str(config_path))
                assert config_manager.get("CB_USERNAME") == "file_user"
                assert config_manager.get("CB_TOKEN") == "file_token"

    def test_load_env_and_file_combined(self) -> None:
        """Test loading configuration from both environment variables and a file."""
        with (
            patch(
                "os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d
            ),
            TemporaryDirectory() as tempdir,
        ):
            config_path = Path(tempdir) / "config.yaml"
            config_path.write_text(
                """
            CB_TOKEN: "file_token"
            """,
                encoding="utf-8",
            )

            config_manager = ConfigManager(config_file=str(config_path))
            assert config_manager.get("CB_USERNAME") == "env_user"
            assert config_manager.get("CB_TOKEN") == "file_token"

    def test_env_overrides_file(self) -> None:
        """Test that environment variables override the values in the configuration file."""
        with patch(
            "os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d
        ):
            with TemporaryDirectory() as tempdir:
                config_path = Path(tempdir) / "config.yaml"
                config_path.write_text(
                    """
                CB_USERNAME: "file_user"
                CB_TOKEN: "file_token"
                """,
                    encoding="utf-8",
                )

                config_manager = ConfigManager(config_file=str(config_path))
                assert config_manager.get("CB_USERNAME") == "env_user"
                assert config_manager.get("CB_TOKEN") == "file_token"

    def test_get_with_default(self) -> None:
        """Test the get method with a default value."""
        config_manager = ConfigManager()
        assert config_manager.get("NON_EXISTENT_KEY", "default_value") == "default_value"


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


class TestMain:
    """Tests for the main method."""

    def test_start_polling_verbose(self, mocker: Any) -> None:
        """Test the start_polling function with verbose output."""
        with (
            suppress(KeyboardInterrupt),
            pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."),
        ):
            asyncio.run(
                start_polling(
                    USERNAME,
                    TOKEN,
                    api_timeout=10,
                    event_handler=mocker.Mock(),
                    testbed=False,
                    verbose=True,
                )
            )
        assert logging.getLogger().level == logging.DEBUG

    @pytest.mark.asyncio
    async def test_fetch_events_returns_none(self, mocker: Any) -> None:
        """Test start_polling when fetch_events returns None."""
        mocker.patch.dict("os.environ", {"CB_USERNAME": "testuser", "CB_TOKEN": "testtoken"})

        mock_fetch_events = AsyncMock(return_value=None)
        mock_client = mocker.patch.object(
            ChaturbateClient, "__aenter__", return_value=mocker.Mock()
        )
        mock_client.return_value.fetch_events = mock_fetch_events

        await start_polling(
            username="testuser",
            token="testtoken",  # noqa: S106
            api_timeout=10,
            event_handler=mocker.Mock(),
            testbed=False,
            verbose=False,
        )
        mock_fetch_events.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_username_or_token(self, mocker: Any, caplog: Any) -> None:
        """Test start_polling when username or token is missing."""
        mocker.patch.dict("os.environ", {"CB_USERNAME": "", "CB_TOKEN": ""})

        with caplog.at_level(logging.ERROR):
            await start_polling(
                username="",
                token="",
                api_timeout=10,
                testbed=False,
                verbose=False,
                event_handler=mocker.Mock(),
            )
        assert (
            "CB_USERNAME and CB_TOKEN must be provided as arguments or environment variables."
            in caplog.text
        )


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
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test timeout handling."""
        http_client_mock.side_effect = TimeoutException(
            message="Timeout", request=Request("GET", TEST_URL)
        )
        with pytest.raises(TimeoutException):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_fetch_events_influxdb_error(
        self, mocker: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetch_events method when InfluxDB write fails."""
        mocker.patch.object(
            chaturbate_client.influxdb_handler,
            "write_event",
            side_effect=Exception("InfluxDB Error"),
        )
        with pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."):
            await chaturbate_client.fetch_events()

    @pytest.mark.asyncio
    async def test_fetch_events_timeout(
        self, mocker: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetch_events method when a timeout occurs."""
        mocker.patch.object(
            chaturbate_client.client, "get", side_effect=ReadTimeout("Request timed out")
        )
        with pytest.raises(ReadTimeout):
            await chaturbate_client.fetch_events()

    @pytest.mark.asyncio
    async def test_fetch_events_unhandled_exception(self, mocker: Any) -> None:
        """Test fetch_events method handles unhandled exceptions properly."""
        mocker.patch("httpx.AsyncClient.get", side_effect=Exception("Unhandled error"))

        with pytest.raises(Exception, match="Unhandled error"):
            async with ChaturbateClient(USERNAME, TOKEN) as client:
                await client.fetch_events()


class TestURLConstruction:
    """Tests for URL construction."""

    @pytest.mark.asyncio
    async def test_url_construction(self, chaturbate_client: ChaturbateClient) -> None:
        """Test URL construction."""
        url = chaturbate_client._construct_url()
        assert url == TEST_URL, "URL should be correctly constructed."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout(self, chaturbate_client: ChaturbateClient) -> None:
        """Test URL construction with timeout."""
        chaturbate_client.timeout = 10
        url = chaturbate_client._construct_url()
        assert url == f"{TEST_URL}?timeout=10", "URL should be correctly constructed with timeout."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout_zero(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout zero."""
        chaturbate_client.timeout = 0
        url = chaturbate_client._construct_url()
        assert url == TEST_URL, "URL should be correctly constructed without timeout."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout_none(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout None."""
        chaturbate_client.timeout = None
        url = chaturbate_client._construct_url()
        assert url == TEST_URL, "URL should be correctly constructed without timeout."


class TestMessageFormatting:
    """Tests for message formatting."""

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
    async def test_events(
        self,
        example_user: User,
        media_photos: Media,
        tip_example: Tip,
        event_method: str,
        event_data_func: Callable,
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
            ("example message", False, "tipped 100 tokens with message: 'example message'"),
            ("", False, "tipped 100 tokens "),
            (
                "example message",
                True,
                "tipped 100 tokens anonymously with message: 'example message'",
            ),
        ],
    )
    async def test_tip_variants(
        self,
        example_user: User,
        tip_example: Tip,
        tip_message: str,
        is_anon: bool,
        expected_suffix: str,
    ) -> None:
        """Test the formatting of tip events."""
        tip_example.message = tip_message
        tip_example.is_anon = is_anon
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
        ],
    )
    async def test_unknown_and_special_events(
        self, event_method: str, expected_message: str
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
            tip=Tip(tokens=100, message="example message", isAnon=False),
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
        if event_data.user:
            assert event_data.user.username == "example_user"
            assert event_data.user.in_fanclub is False

        if event_data.tip:
            assert event_data.tip.tokens == 100
            assert event_data.tip.message == "example message"
            assert event_data.tip.is_anon is False

        if event_data.media:
            assert event_data.media.id == 1
            assert event_data.media.name == "photoset1"
            assert event_data.media.type == MediaType.PHOTOS
            assert event_data.media.tokens == 25

        if event_data.message:
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
        if event.object.user:
            assert event.object.user.username == "example_user"
        assert event.id == "UNIQUE_EVENT_ID"

    def test_tip_model(self) -> None:
        """Test the Tip model."""
        tip = Tip(tokens=100, message="example message", isAnon=False)
        assert tip.tokens == 100
        assert tip.message == "example message"
        assert tip.is_anon is False

    def test_media_model(self) -> None:
        """Test the Media model."""
        media = Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)
        assert media.id == 1
        assert media.name == "photoset1"
        assert media.type == MediaType.PHOTOS
        assert media.tokens == 25

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
            assert response.status_code == 200

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

    def test_format_tip_event_unknown_tip_event(self) -> None:
        """Test formatting a tip event with an unknown tip event."""
        message = format_tip_event(
            Event(
                method="tip",
                object=EventData(broadcaster="example_broadcaster", user=None, tip=None),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "Unknown tip event"

    def test_format_message_event_unknown_message_event(self) -> None:
        """Test formatting a message event with an unknown message event."""
        message = format_message_event(
            Event(
                method="unknown",
                object=EventData(broadcaster="example_broadcaster", user=None, tip=None),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "Unknown message event"

    def test_format_media_purchase_event_unknown_media_purchase_event(self) -> None:
        """Test formatting a media purchase event with an unknown media purchase event."""
        message = format_media_purchase_event(
            Event(
                method="mediaPurchase",
                object=EventData(broadcaster="example_broadcaster", user=None, media=None),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "Unknown media purchase event"


class TestEventFetching:
    """Tests for fetching events."""

    @pytest.mark.asyncio
    async def test_fetch_events_undefined_json(
        self, chaturbate_client: ChaturbateClient, http_client_mock: Any
    ) -> None:
        """Test fetching events with undefined JSON."""
        request = Request("GET", TEST_URL)
        response_content = b'{"not": "json", "nextUrl": "https://example.com"}'
        http_client_mock.return_value = Response(200, content=response_content, request=request)

        with pytest.raises(ValidationError, match="1 validation error for EventsAPIResponse"):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
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
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient, caplog: Any
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
            (HttpStatusCode.BAD_REQUEST, False),
            (HttpStatusCode.UNAUTHORIZED, False),
            (HttpStatusCode.FORBIDDEN, False),
            (HttpStatusCode.NOT_FOUND, False),
        ],
    )
    def test_http_status_error(self, status_code: int, expected: bool) -> None:
        """Test need_retry with HTTPStatusError exceptions."""
        exception = HTTPStatusError(
            message="Error",
            request=Request("GET", "https://error.url.com"),
            response=Response(status_code),
        )
        assert ChaturbateUtils().need_retry(exception) == expected

    def test_non_http_status_error(self) -> None:
        """Test need_retry with a non-HTTPStatusError exception."""
        exception = TimeoutException("Timeout occurred")
        assert not ChaturbateUtils().need_retry(exception)


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

    def test_sanitize_url(self) -> None:
        """Test that the sanitize_url function masks sensitive information."""
        url = "https://eventsapi.chaturbate.com/events/username/token/"
        sanitized = sanitize_url(url)
        assert sanitized == "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/"

    def test_sanitize_url_filter_with_url_in_message(self) -> None:
        """Test that the filter sanitizes a URL in the message."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="https://eventsapi.chaturbate.com/events/username/token/",
            args=(),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/"

    def test_sanitize_url_filter_with_plain_message(self) -> None:
        """Test that the filter does not modify a message without a URL."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="This is a log message.",
            args=(),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "This is a log message."

    def test_sanitize_url_filter_with_args(self) -> None:
        """Test that the filter sanitizes URLs in the arguments."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message with args",
            args=("https://eventsapi.chaturbate.com/events/username/token/", 123, "no-url"),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.args == (
            "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/",
            "123",
            "no-url",
        )

    def test_sanitize_url_filter_with_none_args(self) -> None:
        """Test that the filter works when args is None."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="This is a log message with no args.",
            args=None,
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "This is a log message with no args."
        assert log_record.args is None

    def test_sanitize_url_filter_with_empty_args_tuple(self) -> None:
        """Test that the filter handles an empty args tuple."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message with empty args tuple",
            args=(),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "Message with empty args tuple"
        assert log_record.args == ()

    def test_sanitize_url_filter_with_mixed_args(self) -> None:
        """Test that the filter sanitizes URLs and handles non-string args."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message with mixed args",
            args=(
                "https://eventsapi.chaturbate.com/events/username/token/",
                123,
                None,
                "https://example.com/no-token/",
            ),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.args == (
            "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/",
            "123",
            "None",
            "https://example.com/no-token/",
        )

    def test_sanitize_url_filter_with_string_message(self) -> None:
        """Test that the filter sanitizes a string message."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User accessed the URL: events/username/token/",
            args=(),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "User accessed the URL: events/USERNAME/TOKEN/"

    def test_sanitize_url_filter_with_args_string(self) -> None:
        """Test that the filter sanitizes a URL in args when message is not a URL."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Accessing events",
            args=("events/username/token/",),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "Accessing events"
        assert log_record.args == ("events/USERNAME/TOKEN/",)

    def test_sanitize_url_filter_with_multiple_args(self) -> None:
        """Test that the filter sanitizes URLs in multiple args."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User actions",
            args=(
                "events/username/token/",
                "other_arg",
                "another/events/username/token/",
            ),
            exc_info=None,
        )

        assert _filter.filter(log_record)
        assert log_record.msg == "User actions"
        assert log_record.args == (
            "events/USERNAME/TOKEN/",
            "other_arg",
            "another/events/USERNAME/TOKEN/",
        )

    def test_custom_formatter(self) -> None:
        """Test the CustomFormatter to ensure it formats log records properly."""
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
