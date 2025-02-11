"""Factory for creating event handlers."""

import logging

from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
from chaturbate_poller.handlers.database_handler import DatabaseEventHandler
from chaturbate_poller.handlers.event_handler import EventHandler
from chaturbate_poller.handlers.logging_handler import LoggingEventHandler

logger = logging.getLogger(__name__)


def create_event_handler(handler_type: str) -> EventHandler:
    """Create an event handler.

    Args:
        handler_type (str): The type of event handler to create.

    Returns:
        EventHandler: The appropriate event handler based on the type.

    Raises:
        ValueError: If an unknown handler type is passed.
    """
    if handler_type == "database":
        influxdb_handler = InfluxDBHandler()
        return DatabaseEventHandler(influxdb_handler)
    if handler_type == "logging":
        return LoggingEventHandler()
    msg = f"Unknown handler type: {handler_type}"
    raise ValueError(msg)
