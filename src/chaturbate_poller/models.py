# chaturbate_poller/src/chaturbate_poller/models.py
"""Pydantic models for the Chaturbate Events API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Media(BaseModel):
    """Model for the Media object."""

    id: int
    """int: The media ID."""
    type: str
    """str: The media type. (photos, videos)"""
    name: str
    """str: The media name."""
    tokens: int
    """int: The media tokens."""


class Message(BaseModel):
    """Model for the Message object."""

    color: str
    """str: The message color."""
    bg_color: str | None = Field(None, alias="bgColor")
    """str: The message background color. (Optional)"""
    message: str
    """str: The message."""
    font: str
    """str: The message font."""
    from_user: str | None = Field(None, alias="fromUser")
    """str: The message sender. (Optional)"""
    to_user: str | None = Field(None, alias="toUser")
    """str: The message receiver. (Optional)"""


class Tip(BaseModel):
    """Model for the Tip object."""

    tokens: int
    """int: The tip tokens."""
    is_anon: bool = Field(..., alias="isAnon")
    """bool: Whether the tip is anonymous."""
    message: str
    """str: The tip message."""


class User(BaseModel):
    """Model for the User object."""

    username: str
    """str: The username."""
    in_fanclub: bool = Field(..., alias="inFanclub")
    """bool: Whether the user is in the fanclub."""
    has_tokens: bool = Field(..., alias="hasTokens")
    """bool: Whether the user has tokens."""
    is_mod: bool = Field(..., alias="isMod")
    """bool: Whether the user is a moderator."""
    recent_tips: str = Field(..., alias="recentTips")
    """str: The user's recent tips."""
    gender: str
    """str: The user's gender."""
    subgender: str | None = None
    """str: The user's subgender. (Optional)"""


class CombinedObject(BaseModel):
    """Model for the CombinedObject object."""

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

    method: str
    """str: The event method."""
    object: CombinedObject = Field(..., alias="object")
    """CombinedObject: The event object."""
    id: str
    """str: The event ID."""


class EventsAPIResponse(BaseModel):
    """Model for the EventsAPIResponse object."""

    events: list[Event]
    """list[Event]: The events."""
    next_url: str | None = Field(..., alias="nextUrl")
    """str: The next URL."""


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
