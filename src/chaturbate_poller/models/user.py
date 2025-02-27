"""This module contains the User model for the Chaturbate Events API."""

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a user in the Chaturbate Events API."""

    username: str
    in_fanclub: bool = Field(alias="inFanclub")
    has_tokens: bool = Field(alias="hasTokens")
    is_mod: bool = Field(alias="isMod")
    recent_tips: str = Field(alias="recentTips", pattern="^(none|some|few|lots|tons)$")
    gender: str
    subgender: str = ""
