"""Models for the chat or private message system."""

from pydantic import BaseModel, Field, computed_field


class Message(BaseModel):
    """Model for the Message object."""

    color: str = Field(..., description="The message color.")
    """str: The message color."""
    bg_color: str | None = Field(
        None, alias="bgColor", description="The message background color. (Optional)"
    )
    """str | None: The message background color. (Optional)"""
    message: str = Field(..., description="The message.")
    """str: The message."""
    font: str = Field(..., description="The message font.")
    """str: The message font."""
    from_user: str | None = Field(
        None, alias="fromUser", description="The message sender. (Optional)"
    )
    """str | None: The message sender. (Optional)"""
    to_user: str | None = Field(
        None, alias="toUser", description="The message receiver. (Optional)"
    )
    """str | None: The message receiver. (Optional)"""

    # See https://docs.pydantic.dev/2.0/usage/computed_fields/
    # for the rationale behind ignoring the type errors below.
    @computed_field  # type: ignore[misc]
    @property
    def is_private_message(self) -> bool:
        """Determines if the message is a private message.

        A private message typically has 'from_user' and 'to_user' fields.
        """
        return self.from_user is not None and self.to_user is not None

    @computed_field  # type: ignore[misc]
    @property
    def is_chat_message(self) -> bool:
        """Determines if the message is a public chat message.

        A public chat message typically does NOT have 'from_user' or 'to_user' fields
        (or at least not both, as 'to_user' would be irrelevant in a public chat).
        """
        return self.from_user is None and self.to_user is None
