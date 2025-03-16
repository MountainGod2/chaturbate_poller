"""Models for the response from the Chaturbate Events API."""

import pydantic

from chaturbate_poller.models.event import Event


class EventsAPIResponse(pydantic.BaseModel):
    """Represents the response from the Chaturbate Events API."""

    events: list[Event]
    next_url: str | None = pydantic.Field(default=None, alias="nextUrl", pattern="^https?://")
