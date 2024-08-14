# ruff: noqa: S101
"""Tests for the event handlers."""

import pytest

from chaturbate_poller.event_handlers import (
    DatabaseEventHandler,
    LoggingEventHandler,
    create_event_handler,
)
from chaturbate_poller.models import Event, EventData, Gender, Tip, User


@pytest.fixture()
def mock_influxdb_handler(mocker) -> None:  # noqa: ANN001
    """Fixture for the InfluxDB handler."""
    return mocker.Mock()


@pytest.fixture()
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
                gender=Gender(
                    "m",
                ),
            ),
            tip=Tip(
                tokens=100,
                message="test message",
                isAnon=False,
            ),
        ),
        id="1",
    )


def test_create_event_handler_logging() -> None:
    """Test the create_event_handler function with the logging handler."""
    handler = create_event_handler("logging")
    assert isinstance(handler, LoggingEventHandler)


def test_create_event_handler_database() -> None:
    """Test the create_event_handler function with the database handler."""
    handler = create_event_handler("database")
    assert isinstance(handler, DatabaseEventHandler)


@pytest.mark.asyncio()
async def test_logging_event_handler(sample_event, caplog) -> None:  # noqa: ANN001
    """Test the LoggingEventHandler."""
    handler = LoggingEventHandler()
    await handler.handle_event(sample_event)

    assert "test_user tipped 100 tokens with message: 'test message'" in caplog.text


@pytest.mark.asyncio()
async def test_database_event_handler(mock_influxdb_handler, sample_event) -> None:  # noqa: ANN001
    """Test the DatabaseEventHandler."""
    handler = DatabaseEventHandler(mock_influxdb_handler)
    await handler.handle_event(sample_event)

    mock_influxdb_handler.write_event.assert_called_once_with(
        "chaturbate_events", sample_event.model_dump()
    )


@pytest.mark.asyncio()
async def test_create_event_handler_unknown() -> None:
    """Test the create_event_handler function with an unknown handler."""
    with pytest.raises(ValueError, match="Unknown handler type: unknown"):
        create_event_handler("unknown")
