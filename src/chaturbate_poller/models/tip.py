"""This module contains the Tip model for the Chaturbate Events API."""

from typing import Any

from pydantic import BaseModel, Field, model_validator


class Tip(BaseModel):
    """Represents a tip event from the Chaturbate Events API."""

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
