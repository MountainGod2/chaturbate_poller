"""Models for the response from the Chaturbate Events API."""

from pydantic import BaseModel, Field

from chaturbate_poller.models.event import Event


class EventsAPIResponse(BaseModel):
    """Represents the response from the Chaturbate Events API."""

    events: list[Event]
    """list[Event]: List of events returned by the API."""
    next_url: str | None = Field(default=None, alias="nextUrl", pattern="^https?://")
    """str | None: The URL for the next page of events, if available."""
