"""Models for the chat or private message system."""

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a chat or private message."""

    color: str
    bg_color: str | None = Field(None, alias="bgColor")
    message: str = Field(..., min_length=1)
    font: str
    from_user: str | None = Field(None, alias="fromUser")
    to_user: str | None = Field(None, alias="toUser")
