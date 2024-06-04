"""Exceptions for Chaturbate Event Listener."""


class ChaturbateError(Exception):
    """Base exception for Chaturbate Event Listener."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message = message


class UnauthorizedError(ChaturbateError):
    """Exception for unauthorized access."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)


class ForbiddenError(ChaturbateError):
    """Exception for forbidden access."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)


class NotFoundError(ChaturbateError):
    """Exception for resource not found."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
