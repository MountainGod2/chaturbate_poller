"""Tests for the errors module."""

import pytest

from chaturbate_event_listener.errors import (
    ChaturbateEventListenerError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ChaturbateEventListenerError, "Base exception for Chaturbate Event Listener."),
        (UnauthorizedError, "Exception for unauthorized access."),
        (ForbiddenError, "Exception for forbidden access."),
        (NotFoundError, "Exception for resource not found."),
    ],
)
def test_error_messages(error: type[Exception], expected: str) -> None:
    """Test the error messages."""
    assert error.__doc__ == expected
