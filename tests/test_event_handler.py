from typing import Any

import pytest

from chaturbate_poller.event_handler import (
    DatabaseEventHandler,
    LoggingEventHandler,
    create_event_handler,
)
from chaturbate_poller.models import (
    Event,
)


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
