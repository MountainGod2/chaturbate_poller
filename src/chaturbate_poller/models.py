"""Pydantic models for the Chaturbate Events API."""

from __future__ import annotations

from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
)


class MediaType(Enum):
    """Enumeration for the media type."""

    PHOTOS = "photos"
    """str: The media type is photos."""
    VIDEOS = "videos"
    """str: The media type is videos."""


class Gender(Enum):
    """Enumeration for the user's gender."""

    MALE = "m"
    """str: The user is male."""
    FEMALE = "f"
    """str: The user is female."""
    TRANS = "t"
    """str: The user is trans."""
    COUPLE = "c"
    """str: The user is a couple."""


class Subgender(Enum):
    """Enumeration for the user's subgender."""

    NONE = ""
    TF = "tf"
    TM = "tm"
    TN = "tn"


class Media(BaseModel):
    """Model for the Media object."""

    id: int = Field(..., description="The media ID.")
    """int: The media ID."""
    type: MediaType = Field(..., description="The media type.")
    """MediaType: The media type."""
    name: str = Field(..., description="The media name.")
    """str: The media name."""
    tokens: int = Field(..., description="The media tokens.")
    """int: The media tokens."""


class Message(BaseModel):
    """Model for the Message object."""

    color: str = Field(..., description="The message color.")
    """str: The message color."""
    bg_color: str | None = Field(
        None, alias="bgColor", description="The message background color. (Optional)"
    )
    """str: The message background color. (Optional)"""
    message: str = Field(..., description="The message.")
    """str: The message."""
    font: str = Field(..., description="The message font.")
    """str: The message font."""
    from_user: str | None = Field(
        None, alias="fromUser", description="The message sender. (Optional)"
    )
    """str: The message sender. (Optional)"""
    to_user: str | None = Field(
        None, alias="toUser", description="The message receiver. (Optional)"
    )
    """str: The message receiver. (Optional)"""


class Tip(BaseModel):
    """Model for the Tip object."""

    tokens: int = Field(..., description="The number of tokens included in the tip.")
    """int: The number of tokens included in the tip."""
    is_anon: bool = Field(
        ..., alias="isAnon", description="Whether the tip is made anonymously."
    )
    """bool: Whether the tip is made anonymously."""
    message: str = Field(..., description="A message accompanying the tip.")
    """str: A message accompanying the tip."""

    @field_validator("tokens")
    @classmethod
    def validate_tokens(cls, v: int) -> int:
        """Validate the tokens value."""
        if v < 1:
            msg = "Tokens must be greater than 0."
            raise ValueError(msg)
        return v


class User(BaseModel):
    """Model for the User object."""

    username: str = Field(..., description="The username.")
    """str: The username."""
    in_fanclub: bool = Field(
        ..., alias="inFanclub", description="Whether the user is in the fanclub."
    )
    """bool: Whether the user is in the fanclub."""
    has_tokens: bool = Field(
        ..., alias="hasTokens", description="Whether the user has tokens."
    )
    """bool: Whether the user has tokens."""
    is_mod: bool = Field(
        ..., alias="isMod", description="Whether the user is a moderator."
    )
    """bool: Whether the user is a moderator."""
    recent_tips: str = Field(
        ..., alias="recentTips", description="The user's recent tips."
    )
    """str: The user's recent tips."""
    gender: Gender = Field(..., description="The user's gender.")
    """Gender: The user's gender."""
    subgender: Subgender = Field(
        default=Subgender.NONE, description="The user's subgender."
    )


class EventData(BaseModel):
    """Model for the EventData object."""

    broadcaster: str | None = None
    """str: The broadcaster."""
    user: User | None = None
    """User: The user."""
    media: Media | None = None
    """Media: The media."""
    tip: Tip | None = None
    """Tip: The tip."""
    message: Message | None = None
    """Message: The message."""
    subject: str | None = None
    """str: The subject."""


class Event(BaseModel):
    """Model for the Event object."""

    method: str = Field(..., description="The event method.")
    """str: The event method."""
    object: EventData = Field(..., alias="object", description="The event data.")
    """EventData: The event object."""
    id: str = Field(..., description="The event ID.")
    """str: The event ID."""


class EventsAPIResponse(BaseModel):
    """Model for the EventsAPIResponse object."""

    events: list[Event]
    """list[Event]: A list containing the event objects."""
    next_url: HttpUrl | None = Field(..., alias="nextUrl", description="The next URL.")


json_string = """
{
    "events":[
        {
            "method":"mediaPurchase",
            "object":{
				"broadcaster": "example_broadcaster",
				"user": {
					"username": "example_user",
					"inFanclub": false,
					"gender": "m",
					"hasTokens": true,
					"recentTips": "none",
					"isMod": false
				},
				"media": {
					"id": 1,
					"name": "photoset1",
					"type": "photos",
					"tokens": 25
                }
            },
            "id":"UNIQUE_EVENT_ID"
        }
    ],
    "nextUrl":"https://eventsapi.chaturbate.com/events/REDACTED_BROADCASTER/REDACTED_API_TOKEN/?i=UNIQUE_EVENT_ID&timeout=10"
}
"""
"""str: A JSON string representing the EventsAPIResponse object."""
