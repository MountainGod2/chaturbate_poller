"""This module contains the data models for the Chaturbate Events API."""

from pydantic import BaseModel

from chaturbate_poller.models.media import Media
from chaturbate_poller.models.message import Message
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User


class EventData(BaseModel):
    """Represents the data payload of an event from the Chaturbate Events API."""

    broadcaster: str | None = None
    """str | None: The username of the broadcaster associated with the event."""
    user: User | None = None
    tip: Tip | None = None
    media: Media | None = None
    message: Message | None = None
    subject: str | None = None
