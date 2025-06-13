"""Models for media purchase events."""

from pydantic import BaseModel, Field


class Media(BaseModel):
    """Represents a media purchase event."""

    id: int
    """int: The unique identifier for the media purchase."""
    type: str = Field(default=..., pattern="^(photos|video)$")
    """str: The type of media purchased, either 'photos' or 'video'."""
    name: str
    """str: The name of the media purchased."""
    tokens: int
    """int: The number of tokens spent on the media purchase."""
