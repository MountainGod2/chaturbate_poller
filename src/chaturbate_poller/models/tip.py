"""This module contains the Tip model for the Chaturbate Events API."""

from __future__ import annotations

import pydantic


class Tip(pydantic.BaseModel):
    """Represents a tip event from the Chaturbate Events API."""

    tokens: int = pydantic.Field(default=..., ge=1)
    is_anon: bool = pydantic.Field(alias="isAnon")
    message: str
