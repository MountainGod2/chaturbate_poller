"""This module contains the data models for the Chaturbate Events API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic

if TYPE_CHECKING:
    from chaturbate_poller.models.media import Media
    from chaturbate_poller.models.message import Message
    from chaturbate_poller.models.tip import Tip
    from chaturbate_poller.models.user import User


class EventData(pydantic.BaseModel):
    """Represents the data payload of an event from the Chaturbate Events API."""

    broadcaster: str | None = None
    user: User | None = None
    tip: Tip | None = None
    media: Media | None = None
    message: Message | None = None
    subject: str | None = None
