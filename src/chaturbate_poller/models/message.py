"""Models for the chat or private message system."""

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a chat or private message."""

    color: str
    bg_color: str | None = Field(default=None, alias="bgColor")
    message: str
    font: str
    from_user: str | None = Field(default=None, alias="fromUser")
    to_user: str | None = Field(default=None, alias="toUser")
