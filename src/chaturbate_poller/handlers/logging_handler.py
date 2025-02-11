"""Logging event handler implementation."""

import logging

from chaturbate_poller.handlers.event_handler import EventHandler
from chaturbate_poller.models.event import Event
from chaturbate_poller.utils.format_messages import format_message

logger = logging.getLogger(__name__)


class LoggingEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for logging events."""

    async def handle_event(self, event: Event) -> None:
        """Handle an event by logging it."""
        logger.debug("Handling event for logging: %s", event.method)
        if message := format_message(event):  # pragma: no branch
            logger.info(message)
