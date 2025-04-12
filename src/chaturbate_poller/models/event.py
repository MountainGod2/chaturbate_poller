"""Event model for the Chaturbate Events API."""

import pydantic

from chaturbate_poller.models.event_data import EventData

METHOD_PATTERN: str = str(
    "^(broadcastStart|broadcastStop|"  # pyright: ignore[reportImplicitStringConcatenation]
    "chatMessage|fanclubJoin|follow|"
    "mediaPurchase|privateMessage|"
    "roomSubjectChange|tip|unfollow|"
    "userEnter|userLeave)$"
)
"""str: The pattern for the allowed event methods."""


class Event(pydantic.BaseModel):
    """Represents an event from the Chaturbate Events API."""

    method: str = pydantic.Field(
        default=...,
        pattern=METHOD_PATTERN,
        description="The event method.",
    )
    object: EventData
    id: str
