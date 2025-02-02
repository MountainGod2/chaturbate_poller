"""This module contains the event handlers for the Chaturbate poller."""

import logging
from abc import ABC, abstractmethod

from chaturbate_poller.format_messages import format_message
from chaturbate_poller.influxdb_handler import InfluxDBHandler
from chaturbate_poller.models import Event

logger = logging.getLogger(__name__)
"""logging.Logger: The module-level logger."""


class EventHandler(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for event handlers."""

    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        """Handle an event.

        Args:
            event (Event): The event to be handled.
        """


class DatabaseEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for writing events to a database."""

    def __init__(self, influxdb_handler: InfluxDBHandler) -> None:
        """Initialize the database event handler.

        Args:
            influxdb_handler (InfluxDBHandler): The handler to interact with InfluxDB.
        """
        self.influxdb_handler = influxdb_handler

    async def handle_event(self, event: Event) -> None:
        """Handle an event by writing it to the database.

        Args:
            event (Event): The event to be written to the database.
        """
        logger.debug("Handling event for database: %s", event.method)
        self.influxdb_handler.write_event("chaturbate_events", event.model_dump())


class LoggingEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for logging events."""

    def __init__(self) -> None:
        """Initialize the logging event handler."""

    async def handle_event(self, event: Event) -> None:  # noqa: PLR6301, RUF100
        """Handle an event by logging it.

        Args:
            event (Event): The event to be logged.
        """
        logger.debug("Handling event for logging: %s", event.method)
        message = format_message(event)
        logger.info(message)


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
