"""This module contains the User model for the Chaturbate Events API."""

from typing import Any

from pydantic import BaseModel, Field, model_validator


class User(BaseModel):
    """Represents a user in the Chaturbate Events API."""

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
        # Added "few" to the valid tips (not documented in the API)
        # https://chaturbate.com/apps/api/docs/objects.html#user
        valid_tips = {"none", "few", "some", "lots", "tons"}
        if values.get("recentTips") not in valid_tips or not values.get("recentTips"):
            msg = "recentTips must be one of: none, some, lots, tons"
            raise ValueError(msg)
        return values
