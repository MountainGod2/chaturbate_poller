"""This module contains the User model for the Chaturbate Events API."""

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a user in the Chaturbate Events API."""

    username: str
    """str: The username of the user."""
    in_fanclub: bool = Field(alias="inFanclub")
    """bool: Indicates if the user is in the fan club."""
    has_tokens: bool = Field(alias="hasTokens")
    """bool: Indicates if the user has tokens."""
    is_mod: bool = Field(alias="isMod")
    """bool: Indicates if the user is a moderator."""
    recent_tips: str = Field(alias="recentTips", pattern="^(none|some|few|lots|tons)$")
    """str: Recent tips status, can be 'none', 'some', 'few', 'lots', or 'tons'."""
    gender: str
    """str: The gender of the user."""
    subgender: str = ""
    """str: The subgender of the user, default is an empty string."""
