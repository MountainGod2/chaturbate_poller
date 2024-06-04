"""Tests for the errors module."""


def test_chaturbate_error_init() -> None:
    """Test the initialization of ChaturbateError."""
    from chaturbate_event_listener.errors import ChaturbateError

    test_message = "Test message"
    error = ChaturbateError(test_message)

    assert error.message == test_message


def test_unauthorized_error_init() -> None:
    """Test the initialization of UnauthorizedError."""
    from chaturbate_event_listener.errors import UnauthorizedError

    test_message = "Test message"
    error = UnauthorizedError(test_message)

    assert error.message == test_message


def test_forbidden_error_init() -> None:
    """Test the initialization of ForbiddenError."""
    from chaturbate_event_listener.errors import ForbiddenError

    test_message = "Test message"
    error = ForbiddenError(test_message)

    assert error.message == test_message


def test_not_found_error_init() -> None:
    """Test the initialization of NotFoundError."""
    from chaturbate_event_listener.errors import NotFoundError

    test_message = "Test message"
    error = NotFoundError(test_message)

    assert error.message == test_message
