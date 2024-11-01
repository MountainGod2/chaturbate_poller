import asyncio
import logging
from logging.config import dictConfig
from typing import Any

import pytest
from pytest_mock import MockerFixture

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.influxdb_handler import InfluxDBHandler
from chaturbate_poller.logging_config import (
    CustomFormatter,
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

from .constants import TOKEN, USERNAME

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
    dictConfig(TEST_LOGGING_CONFIG)
    logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture(scope="module")
def config_manager() -> ConfigManager:
    """Fixture for the ConfigManager."""
    return ConfigManager(env_file=".env.example")


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
    """Fixture for the stop future."""
    return event_loop.create_future()


@pytest.fixture
def signal_handler(
    event_loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]
) -> SignalHandler:
    """Fixture for the SignalHandler."""
    return SignalHandler(loop=event_loop, stop_future=stop_future)


@pytest.fixture(scope="module")
def influxdb_handler() -> InfluxDBHandler:
    """Fixture for InfluxDBHandler."""
    return InfluxDBHandler()


@pytest.fixture
def log_record() -> logging.LogRecord:
    """Fixture to create a log record."""
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
    """Fixture to create a log record with arguments."""
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="User accessed the URL",
        args=("events/user123/token123", 42),
        exc_info=None,
    )
