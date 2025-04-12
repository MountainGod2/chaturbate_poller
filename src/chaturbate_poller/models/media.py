"""Models for media purchase events."""

import pydantic


class Media(pydantic.BaseModel):
    """Represents a media purchase event."""

    id: int
    type: str = pydantic.Field(default=..., pattern="^(photos|video)$")
    name: str
    tokens: int
