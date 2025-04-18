import asyncio
import logging
from logging.config import dictConfig
from typing import Any

import pytest
from pytest_mock import MockerFixture

from chaturbate_poller.config.settings import Settings
from chaturbate_poller.core.client import ChaturbateClient
from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.event_data import EventData
from chaturbate_poller.models.media import Media
from chaturbate_poller.models.message import Message
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User
from chaturbate_poller.utils.signal_handler import SignalHandler

from .constants import TOKEN, USERNAME

TEST_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
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
    dictConfig(TEST_LOGGING_CONFIG)
    logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture(scope="module")
def settings_manager() -> Settings:
    """Fixture for the Settings manager.

    Returns:
        Settings: Settings instance.
    """
    return Settings(_env_file=".env.example")  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]  # type: ignore[call-arg]


@pytest.fixture
def http_client_mock(mocker: MockerFixture) -> Any:  # pyright: ignore[reportExplicitAny]
    """Fixture for mocking the httpx.AsyncClient.get method.

    Args:
        mocker (MockerFixture): Pytest mocker.

    Returns:
        Any: Mocked httpx.AsyncClient.get method.
    """
    mock = mocker.patch("httpx.AsyncClient.get")
    mock.return_value.json = mocker.AsyncMock(return_value={"events": [], "next_url": None})
    return mock


@pytest.fixture
def chaturbate_client() -> ChaturbateClient:
    """Fixture for creating a ChaturbateClient instance.

    Returns:
        ChaturbateClient: ChaturbateClient instance.
    """
    return ChaturbateClient(username=USERNAME, token=TOKEN)


@pytest.fixture
def mock_influxdb_handler(mocker: Any) -> Any:  # pyright: ignore[reportExplicitAny]
    """Fixture for the InfluxDB handler.

    Args:
        mocker (Any): Mocker.

    Returns:
        Any: Mocked InfluxDB handler.
    """
    return mocker.Mock()


@pytest.fixture
def sample_event() -> Event:
    """Fixture for a sample event.

    Returns:
        Event: Sample event.
    """
    return Event(
        method="tip",
        object=EventData(
            user=User(
                username="test_user",
                inFanclub=False,
                hasTokens=True,
                isMod=False,
                recentTips="lots",
                gender="m",
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
    """Fixture for an example User object.

    Returns:
        User: Example User object.
    """
    return User(
        username="example_user",
        inFanclub=False,
        gender="m",
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )


@pytest.fixture
def media_photos() -> Media:
    """Fixture for an example Media object.

    Returns:
        Media: Example Media object.
    """
    return Media(id=1, name="photoset1", type="photos", tokens=25)


@pytest.fixture
def tip_example() -> Tip:
    """Fixture for an example Tip object.

    Returns:
        Tip: Example Tip object.
    """
    return Tip(tokens=100, message="example message", isAnon=False)


@pytest.fixture
def message_example() -> Message:
    """Fixture for an example Message object.

    Returns:
        Message: Example Message object.
    """
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
    """Fixture for the stop future.

    Args:
        event_loop (asyncio.AbstractEventLoop): Event loop.

    Returns:
        asyncio.Future[None]: Stop future.
    """
    return event_loop.create_future()


@pytest.fixture
def signal_handler(
    event_loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]
) -> SignalHandler:
    """Fixture for the SignalHandler.

    Args:
        event_loop (asyncio.AbstractEventLoop): Event loop.
        stop_future (asyncio.Future[None]): Stop future.

    Returns:
        SignalHandler: SignalHandler instance.
    """
    return SignalHandler(loop=event_loop, stop_future=stop_future)


@pytest.fixture(scope="module")
def influxdb_handler() -> InfluxDBHandler:
    """Fixture for InfluxDBHandler.

    Returns:
        InfluxDBHandler: InfluxDBHandler instance.
    """
    return InfluxDBHandler()


@pytest.fixture
def log_record() -> logging.LogRecord:
    """Fixture to create a log record.

    Returns:
        logging.LogRecord: Log record.
    """
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="events/user123/token123",
        args=(),
        exc_info=None,
    )


@pytest.fixture
def log_record_with_args() -> logging.LogRecord:
    """Fixture to create a log record with arguments.

    Returns:
        logging.LogRecord: Log record with arguments.
    """
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="User accessed the URL",
        args=("events/user123/token123", 42),
        exc_info=None,
    )
