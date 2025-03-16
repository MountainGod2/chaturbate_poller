"""This module contains the User model for the Chaturbate Events API."""

import pydantic


class User(pydantic.BaseModel):
    """Represents a user in the Chaturbate Events API."""

    username: str
    in_fanclub: bool = pydantic.Field(alias="inFanclub")
    has_tokens: bool = pydantic.Field(alias="hasTokens")
    is_mod: bool = pydantic.Field(alias="isMod")
    recent_tips: str = pydantic.Field(alias="recentTips", pattern="^(none|some|few|lots|tons)$")
    gender: str
    subgender: str = ""
