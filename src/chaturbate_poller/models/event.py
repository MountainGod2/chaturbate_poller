"""Event model for the Chaturbate Events API."""

from pydantic import BaseModel, ConfigDict, Field

from chaturbate_poller.constants import EventMethod
from chaturbate_poller.models.event_data import EventData


def _create_method_pattern() -> str:
    """Create pattern from EventMethod enum values."""
    methods = "|".join(method.value for method in EventMethod)
    return f"^({methods})$"


METHOD_PATTERN: str = _create_method_pattern()


class Event(BaseModel):
    """Represents an event from the Chaturbate Events API."""

    model_config = ConfigDict(extra="ignore")  # pyright: ignore[reportUnannotatedClassAttribute]

    method: str = Field(pattern=METHOD_PATTERN, description="The event method.")
    object: EventData
    id: str
