from unittest.mock import Mock

import pytest

from chaturbate_poller.event_handler import (
    DatabaseEventHandler,
    LoggingEventHandler,
    create_event_handler,
)
from chaturbate_poller.models import Event


class TestEventHandler:
    """Tests for event handling."""

    def test_create_event_handler(self) -> None:
        """Test creation of event handlers."""
        assert isinstance(create_event_handler("logging"), LoggingEventHandler)
        assert isinstance(create_event_handler("database"), DatabaseEventHandler)

        with pytest.raises(ValueError, match="Unknown handler type: unknown"):
            create_event_handler("unknown")

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
        self, mock_influxdb_handler: Mock, sample_event: Event
    ) -> None:
        """Test DatabaseEventHandler."""
        handler = DatabaseEventHandler(mock_influxdb_handler)
        await handler.handle_event(sample_event)
        mock_influxdb_handler.write_event.assert_called_once_with(
            "chaturbate_events", sample_event.model_dump()
        )
