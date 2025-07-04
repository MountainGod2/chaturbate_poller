"""Database event handler implementation."""

from __future__ import annotations

import logging
import typing

from chaturbate_poller.handlers.event_handler import EventHandler

if typing.TYPE_CHECKING:
    from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
    from chaturbate_poller.models.event import Event

logger = logging.getLogger(__name__)


class DatabaseEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for writing events to a database."""

    def __init__(self, influxdb_handler: InfluxDBHandler) -> None:
        """Initialize the database event handler."""
        self.influxdb_handler: InfluxDBHandler = influxdb_handler

    async def handle_event(self, event: Event) -> None:
        """Handle an event by writing it to the database.

        Args:
            event: The event to be handled.
        """
        logger.debug("Handling event for database: %s", event.method)
        self.influxdb_handler.write_event(measurement="chaturbate_events", data=event.model_dump())
