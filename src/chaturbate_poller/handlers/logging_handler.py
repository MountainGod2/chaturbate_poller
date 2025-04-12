"""Logging event handler implementation."""

from __future__ import annotations

import logging
import typing

from chaturbate_poller.handlers.event_handler import EventHandler
from chaturbate_poller.utils.format_messages import format_message

if typing.TYPE_CHECKING:
    from chaturbate_poller.models.event import Event

logger: logging.Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""


class LoggingEventHandler(EventHandler):  # pylint: disable=too-few-public-methods
    """Event handler for logging events."""

    @typing.override
    async def handle_event(self, event: Event) -> None:
        """Handle an event by logging it."""
        logger.debug("Handling event for logging: %s", event.method)
        if message := format_message(event):  # pragma: no branch
            logger.info(message)
