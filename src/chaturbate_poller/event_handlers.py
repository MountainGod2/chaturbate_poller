"""This module contains the event handlers for the Chaturbate poller."""

import logging
from abc import ABC, abstractmethod

from chaturbate_poller.format_messages import format_message
from chaturbate_poller.influxdb_client import InfluxDBHandler
from chaturbate_poller.models import Event


class EventHandler(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for event handlers."""

    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        """Handle an event."""


class DatabaseEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for writing events to a database."""

    def __init__(self, influxdb_handler: InfluxDBHandler) -> None:
        """Initialize the database event handler."""
        self.influxdb_handler = influxdb_handler

    async def handle_event(self, event: Event) -> None:
        """Handle an event."""
        self.influxdb_handler.write_event("chaturbate_events", event.model_dump())


class LoggingEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for logging events."""

    async def handle_event(self, event: Event) -> None:
        """Handle an event."""
        message = await format_message(event)
        logging.info(message)


def create_event_handler(handler_type: str) -> EventHandler:
    """Create an event handler.

    Args:
        handler_type (str): The type of event handler to create.

    Returns:
        EventHandler: The event handler.
    """
    if handler_type == "database":
        influxdb_handler = InfluxDBHandler()
        return DatabaseEventHandler(influxdb_handler)
    if handler_type == "logging":
        return LoggingEventHandler()
    msg = f"Unknown handler type: {handler_type}"
    raise ValueError(msg)
