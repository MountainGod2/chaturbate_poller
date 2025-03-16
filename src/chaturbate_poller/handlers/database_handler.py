"""Database event handler implementation."""

import logging
import typing

from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
from chaturbate_poller.handlers.event_handler import EventHandler
from chaturbate_poller.models.event import Event

logger: logging.Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""


class DatabaseEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for writing events to a database."""

    def __init__(self, influxdb_handler: InfluxDBHandler) -> None:
        """Initialize the database event handler."""
        self.influxdb_handler: InfluxDBHandler = influxdb_handler

    @typing.override
    async def handle_event(self, event: Event) -> None:
        """Handle an event by writing it to the database."""
        logger.debug("Handling event for database: %s", event.method)
        self.influxdb_handler.write_event(measurement="chaturbate_events", data=event.model_dump())
