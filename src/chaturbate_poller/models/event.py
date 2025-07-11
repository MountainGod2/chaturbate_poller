"""Event model for the Chaturbate Events API."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from chaturbate_poller.constants import EventMethod
from chaturbate_poller.models.event_data import EventData


class Event(BaseModel):
    """Represents an event from the Chaturbate Events API."""

    model_config = ConfigDict(extra="ignore")  # pyright: ignore[reportUnannotatedClassAttribute]

    method: EventMethod = Field(description="The event method.")
    object: EventData
    id: str

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str) -> EventMethod:
        """Validate the event method against the EventMethod enum."""
        try:
            return EventMethod(value)
        except ValueError:
            msg = f"Unknown event method: {value!r}"
            raise ValueError(msg) from None
