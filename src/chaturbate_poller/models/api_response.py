"""Models for the response from the Chaturbate Events API."""

from pydantic import BaseModel, Field

from chaturbate_poller.models.event import Event


class EventsAPIResponse(BaseModel):
    """Represents the response from the Chaturbate Events API."""

    events: list[Event]
    next_url: str | None = Field(default=None, alias="nextUrl", pattern="^https?://")
