"""Models for the chat or private message system."""

from __future__ import annotations

import pydantic


class Message(pydantic.BaseModel):
    """Represents a chat or private message."""

    color: str
    bg_color: str | None = pydantic.Field(default=None, alias="bgColor")
    message: str
    font: str
    from_user: str | None = pydantic.Field(default=None, alias="fromUser")
    to_user: str | None = pydantic.Field(default=None, alias="toUser")
