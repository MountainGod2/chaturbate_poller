import logging
from logging.config import dictConfig
from typing import Any

import pytest
from pytest_mock import MockerFixture

from chaturbate_poller.config.backoff import BackoffConfig
from chaturbate_poller.config.manager import ConfigManager
from chaturbate_poller.constants import EventMethod
from chaturbate_poller.core.client import ChaturbateClient
from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.event_data import EventData
from chaturbate_poller.models.media import Media
from chaturbate_poller.models.message import Message
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User

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


@pytest.fixture
def disabled_backoff_config() -> BackoffConfig:
    """Fixture for creating a disabled BackoffConfig instance for tests.

    Returns:
        BackoffConfig: A BackoffConfig instance with backoff disabled.
    """
    config = BackoffConfig()
    config.disable_for_tests()
    return config


@pytest.fixture(autouse=True)
def disable_backoff_for_tests() -> None:
    """Disable backoff delays for faster test execution.

    Note: This fixture is kept for backward compatibility with existing tests
    that may rely on it, but new tests should use the disabled_backoff_config fixture.
    """
    # This fixture no longer manipulates a global instance
    # The actual backoff behavior is controlled per-client instance
    return


@pytest.fixture(scope="module")
def config_manager() -> ConfigManager:
    """Fixture for the ConfigManager.

    Returns:
        ConfigManager: ConfigManager instance.
    """
    return ConfigManager(env_file=".env.example")


@pytest.fixture
def http_client_mock(mocker: MockerFixture) -> Any:
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
def chaturbate_client(disabled_backoff_config: BackoffConfig) -> ChaturbateClient:
    """Fixture for creating a ChaturbateClient instance.

    Args:
        disabled_backoff_config (BackoffConfig): Disabled backoff configuration for tests.

    Returns:
        ChaturbateClient: ChaturbateClient instance.
    """
    return ChaturbateClient(username=USERNAME, token=TOKEN, backoff_config=disabled_backoff_config)


@pytest.fixture
def mock_influxdb_handler(mocker: Any) -> Any:
    """Fixture for the InfluxDB handler.

    Args:
        mocker (Any): Mocker.

    Returns:
        Any: Mocked InfluxDB handler.
    """
    return mocker.AsyncMock()


@pytest.fixture
def sample_event() -> Event:
    """Fixture for a sample event.

    Returns:
        Event: Sample event.
    """
    return Event(
        method=EventMethod.TIP,
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
def private_message_example() -> Message:
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
def chat_message_example() -> Message:
    """Fixture for an example Message object.

    Returns:
        Message: Example Message object.
    """
    return Message(
        message="example message",
        color="example_color",
        font="example_font",
        bgColor="example_bg_color",
        fromUser=None,
        toUser=None,
    )


@pytest.fixture(scope="module")
def influxdb_handler() -> InfluxDBHandler:
    """Fixture for InfluxDBHandler.

    Returns:
        InfluxDBHandler: InfluxDBHandler instance.
    """
    return InfluxDBHandler()
