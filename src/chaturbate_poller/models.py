"""Pydantic models for the Chaturbate event feed API."""

from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator


class User(BaseModel):
    """Represents a user in the Chaturbate event system."""

    username: str
    in_fanclub: bool = Field(alias="inFanclub")
    has_tokens: bool = Field(alias="hasTokens")
    is_mod: bool = Field(alias="isMod")
    recent_tips: str = Field(alias="recentTips")
    gender: str
    subgender: str = ""

    @model_validator(mode="before")
    @classmethod
    def validate_recent_tips(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates the recent tips value to ensure it is within allowed values.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `recentTips` is not valid.
        """
        valid_tips = {"none", "some", "lots", "tons"}
        if values.get("recentTips") not in valid_tips or not values.get("recentTips"):
            msg = "recentTips must be one of: none, some, lots, tons"
            raise ValueError(msg)
        return values


class Tip(BaseModel):
    """Represents a tip event."""

    tokens: int
    is_anon: bool = Field(alias="isAnon")
    message: str

    @model_validator(mode="before")
    @classmethod
    def validate_tokens(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the token count is non-negative.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `tokens` is negative.
        """
        tokens = values.get("tokens")
        if tokens is not None and tokens <= 1:
            msg = "tokens must be a non-negative integer"
            raise ValueError(msg)
        return values


class Media(BaseModel):
    """Represents a media purchase event."""

    id: int
    type: str
    name: str
    tokens: int

    @model_validator(mode="before")
    @classmethod
    def validate_media_type(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the media type is one of the supported types.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `type` is not valid.
        """
        valid_types = {"photos", "video"}
        if values.get("type") not in valid_types:
            msg = "type must be one of: photos, video"
            raise ValueError(msg)
        return values


class Message(BaseModel):
    """Represents a message in the chat or private message system."""

    color: str
    bg_color: str | None = Field(None, alias="bgColor")
    message: str
    font: str
    from_user: str | None = Field(None, alias="fromUser")
    to_user: str | None = Field(None, alias="toUser")

    @model_validator(mode="before")
    @classmethod
    def validate_message(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the message content is not empty.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `message` is empty.
        """
        if not values.get("message"):
            msg = "message cannot be empty"
            raise ValueError(msg)
        return values


class EventData(BaseModel):
    """Represents the payload of an event."""

    broadcaster: str | None = None
    user: User | None = None
    tip: Tip | None = None
    media: Media | None = None
    message: Message | None = None
    subject: str | None = None


class Event(BaseModel):
    """Represents an event in the Chaturbate system."""

    method: str
    object: EventData
    id: str

    @model_validator(mode="before")
    @classmethod
    def validate_method(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the method is one of the supported event types.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `method` is not valid.
        """
        valid_methods = {
            "broadcastStart",
            "broadcastStop",
            "chatMessage",
            "fanclubJoin",
            "follow",
            "mediaPurchase",
            "privateMessage",
            "roomSubjectChange",
            "tip",
            "unfollow",
            "userEnter",
            "userLeave",
        }
        if values.get("method") not in valid_methods:
            msg = f"method must be one of: {', '.join(valid_methods)}"
            raise ValueError(msg)
        return values


class EventsAPIResponse(BaseModel):
    """Represents the response from the event feed API."""

    events: list[Event]
    next_url: str | None = Field(None, alias="nextUrl")

    @model_validator(mode="before")
    @classmethod
    def validate_url(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the next URL is a valid URL.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `nextUrl` is not a valid URL.
        """
        if values.get("nextUrl") and not urlparse(values["nextUrl"]).scheme:
            msg = "nextUrl must be a valid URL"
            raise ValueError(msg)
        return values
