"""Models for media purchase events."""

from pydantic import BaseModel, Field


class Media(BaseModel):
    """Represents a media purchase event."""

    id: int
    type: str = Field(default=..., pattern="^(photos|video)$")
    name: str
    tokens: int
