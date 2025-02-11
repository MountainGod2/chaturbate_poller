"""Event model for the Chaturbate Events API."""

from typing import Any

from pydantic import BaseModel, model_validator

from chaturbate_poller.models.event_data import EventData


class Event(BaseModel):
    """Represents an event from the Chaturbate Events API."""

    method: str
    object: EventData
    id: str

    @model_validator(mode="before")
    @classmethod
    def validate_method(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the method is one of the supported event types.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `method` is not valid.
        """
        valid_methods = {
            "broadcastStart",
            "broadcastStop",
            "chatMessage",
            "fanclubJoin",
            "follow",
            "mediaPurchase",
            "privateMessage",
            "roomSubjectChange",
            "tip",
            "unfollow",
            "userEnter",
            "userLeave",
        }
        if values.get("method") not in valid_methods:
            msg = f"method must be one of: {', '.join(valid_methods)}"
            raise ValueError(msg)
        return values
