"""This module contains the event handlers for the Chaturbate poller."""

import logging
from abc import ABC, abstractmethod

from chaturbate_poller.models.event import Event

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
