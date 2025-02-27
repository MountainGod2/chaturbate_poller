"""This module contains the Tip model for the Chaturbate Events API."""

from pydantic import BaseModel, Field


class Tip(BaseModel):
    """Represents a tip event from the Chaturbate Events API."""

    tokens: int = Field(..., ge=1)
    is_anon: bool = Field(alias="isAnon")
    message: str
