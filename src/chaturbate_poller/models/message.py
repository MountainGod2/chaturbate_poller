"""Models for the chat or private message system."""

from typing import Any

from pydantic import BaseModel, Field, model_validator


class Message(BaseModel):
    """Represents a chat or private message."""

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
