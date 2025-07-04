"""Factory for creating event handlers."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
from chaturbate_poller.handlers.database_handler import DatabaseEventHandler
from chaturbate_poller.handlers.logging_handler import LoggingEventHandler

if TYPE_CHECKING:
    from chaturbate_poller.handlers.event_handler import EventHandler


class HandlerType(str, Enum):
    """Available event handler types."""

    DATABASE = "database"
    LOGGING = "logging"


def create_event_handler(handler_type: HandlerType) -> EventHandler:
    """Create an event handler.

    Args:
        handler_type: The type of event handler to create.

    Returns:
        The appropriate event handler based on the type.
    """
    match handler_type:
        case HandlerType.DATABASE:
            return DatabaseEventHandler(InfluxDBHandler())
        case HandlerType.LOGGING:
            return LoggingEventHandler()
