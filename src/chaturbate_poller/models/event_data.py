"""This module contains the data models for the Chaturbate Events API."""

from pydantic import BaseModel, ConfigDict

from chaturbate_poller.models.media import Media
from chaturbate_poller.models.message import Message
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User


class EventData(BaseModel):
    """Represents the data payload of an event from the Chaturbate Events API."""

    model_config = ConfigDict(extra="ignore")  # pyright: ignore[reportUnannotatedClassAttribute]

    broadcaster: str | None = None
    """str | None: The username of the broadcaster associated with the event."""
    user: User | None = None
    """User | None: The user associated with the event, if applicable."""
    tip: Tip | None = None
    """Tip | None: The tip associated with the event, if applicable."""
    media: Media | None = None
    """Media | None: The media associated with the event, if applicable."""
    message: Message | None = None
    """Message | None: The message associated with the event, if applicable."""
    subject: str | None = None
    """str | None: The subject of the event, if applicable."""
