"""Event model for the Chaturbate Events API."""

from pydantic import BaseModel, Field

from chaturbate_poller.models.event_data import EventData

METHOD_PATTERN: str = str(
    "^(broadcastStart|broadcastStop|"  # pyright: ignore[reportImplicitStringConcatenation]
    "chatMessage|fanclubJoin|follow|"
    "mediaPurchase|privateMessage|"
    "roomSubjectChange|tip|unfollow|"
    "userEnter|userLeave)$"
)
"""str: The pattern for the allowed event methods."""


class Event(BaseModel):
    """Represents an event from the Chaturbate Events API."""

    method: str = Field(
        default=...,
        pattern=METHOD_PATTERN,
        description="The event method.",
    )
    """str: The method of the event, e.g., 'tip', 'follow', etc."""
    object: EventData
    """EventData: The data associated with the event."""
    id: str
    """str: The unique identifier for the event."""
