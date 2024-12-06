"""Pydantic models for the Chaturbate Events API."""

from __future__ import annotations

from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class BaseModelWithEnums(BaseModel):
    """Base model with custom configuration for all models."""

    model_config = {
        "use_enum_values": True,
        "populate_by_name": True,  # Ensures aliases work consistently
    }


class MediaType(str, Enum):
    """Enumeration for the media type."""

    PHOTOS = "photos"
    """str: The media type for photos."""
    VIDEOS = "videos"
    """str: The media type for videos."""


class Gender(str, Enum):
    """Enumeration for the user's gender."""

    MALE = "m"
    """str: The gender for male users."""
    FEMALE = "f"
    """str: The gender for female users."""
    TRANS = "t"
    """str: The gender for transgender users."""
    COUPLE = "c"
    """str: The gender for couples."""


class Subgender(str, Enum):
    """Enumeration for the user's subgender."""

    NONE = ""
    """str: The subgender for users with no subgender."""
    TF = "tf"
    """str: The subgender for transfeminine users."""
    TM = "tm"
    """str: The subgender for transmasculine users."""
    TN = "tn"
    """str: The subgender for transneutral users."""


class Media(BaseModelWithEnums):
    """Model for media objects."""

    id: int = Field(..., description="The media ID.")
    """int: The media ID."""
    type: MediaType = Field(..., description="The media type.")
    """MediaType: The media type."""
    name: str = Field(..., description="The media name.")
    """str: The media name."""
    tokens: int = Field(..., description="The media tokens.")
    """int: The media tokens."""


class Message(BaseModelWithEnums):
    """Model for chat messages."""

    color: str = Field(..., description="The message color.")
    """str: The message color."""
    bg_color: str | None = Field(
        default=None, alias="bgColor", description="The message background color."
    )
    """str | None: The message background color."""
    message: str = Field(..., description="The message content.")
    """str: The message content."""
    font: str = Field(..., description="The font used in the message.")
    """str: The font used in the message."""
    from_user: str | None = Field(
        default=None, alias="fromUser", description="The sender of the message."
    )
    """str | None: The sender of the message."""
    to_user: str | None = Field(
        default=None, alias="toUser", description="The recipient of the message."
    )
    """str | None: The recipient of the message."""


class Tip(BaseModelWithEnums):
    """Model for tips."""

    tokens: int = Field(..., description="The number of tokens in the tip.")
    """int: The number of tokens in the tip."""
    is_anon: bool = Field(..., alias="isAnon", description="Whether the tip is anonymous.")
    """bool: Whether the tip is anonymous."""
    message: str = Field(..., description="A message accompanying the tip.")
    """str: A message accompanying the tip."""

    @field_validator("tokens")
    @classmethod
    def ensure_positive_tokens(cls, v: int) -> int:
        """Ensure the number of tokens is positive."""
        if v < 1:
            msg = f"Tokens must be greater than 0. Got: {v}."
            raise ValueError(msg)
        return v


class User(BaseModelWithEnums):
    """Model for user information."""

    username: str = Field(..., description="The username.")
    """str: The username."""
    in_fanclub: bool = Field(
        ..., alias="inFanclub", description="Whether the user is in the fanclub."
    )
    """bool: Whether the user is in the fanclub."""
    has_tokens: bool = Field(..., alias="hasTokens", description="Whether the user has tokens.")
    """bool: Whether the user has tokens."""
    is_mod: bool = Field(..., alias="isMod", description="Whether the user is a moderator.")
    """bool: Whether the user is a moderator."""
    recent_tips: str = Field(..., alias="recentTips", description="The user's recent tips.")
    """str: The user's recent tips."""
    gender: Gender = Field(..., description="The user's gender.")
    """Gender: The user's gender."""
    subgender: Subgender = Field(default=Subgender.NONE, description="The user's subgender.")
    """Subgender: The user's subgender."""


class EventData(BaseModelWithEnums):
    """Model for event data."""

    broadcaster: str | None = Field(default=None, description="The broadcaster.")
    """str | None: The broadcaster."""
    user: User | None = Field(default=None, description="The user.")
    """User | None: The user."""
    media: Media | None = Field(default=None, description="The media associated with the event.")
    """Media | None: The media associated with the event."""
    tip: Tip | None = Field(default=None, description="The tip data.")
    """Tip | None: The tip data."""
    message: Message | None = Field(default=None, description="The message.")
    """Message | None: The message."""
    subject: str | None = Field(default=None, description="The subject of the event.")
    """str | None: The subject of the event."""


class Event(BaseModelWithEnums):
    """Model for an event."""

    method: str = Field(..., description="The event method.")
    """str: The event method."""
    object: EventData = Field(..., description="The event data.")
    """EventData: The event data."""
    id: str = Field(..., description="The unique identifier for the event.")
    """str: The unique identifier for the event."""


class EventsAPIResponse(BaseModelWithEnums):
    """Model for the API response."""

    events: list[Event] = Field(..., description="A list of events.")
    """list[Event]: A list of events."""
    next_url: str = Field(..., alias="nextUrl", description="The URL for the next page of results.")
    """str: The URL for the next page of results."""

    @field_validator("next_url", mode="before")
    @classmethod
    def validate_next_url(cls, v: str) -> str:
        """Validate that the next_url is a valid URL."""
        result = urlparse(v)
        if not result.scheme or not result.netloc:
            msg = f"Invalid URL: {v}."
            raise ValueError(msg)
        return v
