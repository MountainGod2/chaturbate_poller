"""Event model for the Chaturbate Events API."""

import pydantic

from chaturbate_poller.models.event_data import EventData


class Event(pydantic.BaseModel):
    """Represents an event from the Chaturbate Events API."""

    method: str = pydantic.Field(
        default=...,
        pattern="^(broadcastStart|broadcastStop|chatMessage|fanclubJoin|follow|mediaPurchase|privateMessage|roomSubjectChange|tip|unfollow|userEnter|userLeave)$",  # pylint: disable=line-too-long
    )
    object: EventData
    id: str
