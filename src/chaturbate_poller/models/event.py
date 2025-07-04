"""Event model for the Chaturbate Events API."""

from pydantic import BaseModel, Field

from chaturbate_poller.models.event_data import EventData

METHOD_PATTERN: str = (
    "^(broadcastStart|broadcastStop|chatMessage|fanclubJoin|follow|"
    "mediaPurchase|privateMessage|roomSubjectChange|tip|unfollow|"
    "userEnter|userLeave)$"
)


class Event(BaseModel):
    """Represents an event from the Chaturbate Events API."""

    method: str = Field(pattern=METHOD_PATTERN, description="The event method.")
    object: EventData
    id: str
