"""This module contains the Tip model for the Chaturbate Events API."""

from pydantic import BaseModel, Field


class Tip(BaseModel):
    """Represents a tip event from the Chaturbate Events API."""

    tokens: int = Field(default=..., ge=1)
    """int: The number of tokens tipped."""
    is_anon: bool = Field(alias="isAnon")
    """bool: Indicates if the tip is anonymous."""
    message: str
    """str: The message accompanying the tip."""
