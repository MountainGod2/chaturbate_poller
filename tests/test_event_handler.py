from unittest.mock import AsyncMock

import pytest

from chaturbate_poller.handlers.database_handler import DatabaseEventHandler
from chaturbate_poller.handlers.factory import HandlerType, create_event_handler
from chaturbate_poller.handlers.logging_handler import LoggingEventHandler
from chaturbate_poller.models.event import Event


class TestEventHandler:
    """Tests for event handling."""

    def test_create_event_handler(self) -> None:
        """Test creation of event handlers with enum types."""
        assert isinstance(create_event_handler(HandlerType.LOGGING), LoggingEventHandler)
        assert isinstance(create_event_handler(HandlerType.DATABASE), DatabaseEventHandler)

    @pytest.mark.asyncio
    async def test_logging_event_handler(
        self, sample_event: Event, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test LoggingEventHandler."""
        handler = LoggingEventHandler()
        await handler.handle_event(sample_event)
        assert "test_user tipped 100 tokens with message: 'test message'" in caplog.text

    @pytest.mark.asyncio
    async def test_database_event_handler(
        self, mock_influxdb_handler: AsyncMock, sample_event: Event
    ) -> None:
        """Test DatabaseEventHandler."""
        handler = DatabaseEventHandler(mock_influxdb_handler)
        await handler.handle_event(sample_event)
        mock_influxdb_handler.write_event.assert_called_once_with(
            measurement="chaturbate_events", data=sample_event.model_dump()
        )
