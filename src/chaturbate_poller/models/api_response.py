"""Models for the response from the Chaturbate Events API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic

if TYPE_CHECKING:
    from chaturbate_poller.models.event import Event


class EventsAPIResponse(pydantic.BaseModel):
    """Represents the response from the Chaturbate Events API."""

    events: list[Event]
    next_url: str | None = pydantic.Field(default=None, alias="nextUrl", pattern="^https?://")
