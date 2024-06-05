# src/chaturbate_event_listener/logger.py
"""Utilities for the Chaturbate event listener."""

import re
from typing import Any

from chaturbate_event_listener.logger import logger


def log_incomplete_event(event_name: str, message: dict[str, Any]) -> None:
    """Log an incomplete event."""
    logger.warning(f"Incomplete {event_name} event received: %s", message)


def get_username(message: dict[str, Any]) -> str:
    """Get the username from the message.

    Args:
        message (dict[str, Any]): The event message.

    Returns:
        str: The username.
    """
    return message.get("object", {}).get("user", {}).get("username")


def sanitize_url(url: str) -> str:
    """Sanitize URL to hide sensitive information."""
    patterns = [
        r"(?<=/events/)[^/]+(?=/)",
        r"(?<=/)[a-zA-Z0-9]{20,}(?=/)",
        r"(?<=\?i=)[a-zA-Z0-9-]+(?=&)",
    ]
    for pattern in patterns:
        url = re.sub(pattern, "*****", url)
    return url
