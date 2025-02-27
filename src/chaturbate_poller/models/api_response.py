"""Models for the response from the Chaturbate Events API."""

from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator

from chaturbate_poller.models.event import Event


class EventsAPIResponse(BaseModel):
    """Represents the response from the Chaturbate Events API."""

    events: list[Event]
    next_url: str | None = Field(None, alias="nextUrl", pattern="^https?://")

    @model_validator(mode="before")
    @classmethod
    def validate_url(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the next URL is a valid URL.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `nextUrl` is not a valid URL.
        """
        if values.get("nextUrl") and not urlparse(values["nextUrl"]).scheme:
            msg = "nextUrl must be a valid URL"
            raise ValueError(msg)
        return values
