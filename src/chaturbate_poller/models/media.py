"""Models for media purchase events."""

from typing import Any

from pydantic import BaseModel, model_validator


class Media(BaseModel):
    """Represents a media purchase event."""

    id: int
    type: str
    name: str
    tokens: int

    @model_validator(mode="before")
    @classmethod
    def validate_media_type(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validates that the media type is one of the supported types.

        Args:
            values (dict[str, Any]): The values to validate.

        Returns:
            dict[str, Any]: The validated values.

        Raises:
            ValueError: If `type` is not valid.
        """
        valid_types = {"photos", "video"}
        if values.get("type") not in valid_types:
            msg = "type must be one of: photos, video"
            raise ValueError(msg)
        return values
