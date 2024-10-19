"""Exceptions for the Chaturbate Poller."""


class PollingError(Exception):
    """Base exception raised when there is an error during polling."""

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message (str): The exception message.
        """
        super().__init__(message)


class AuthenticationError(PollingError):
    """Exception raised when there is an authentication failure."""

    def __init__(self, message: str = "Invalid token provided.") -> None:
        """Initialize the exception.

        Args:
            message (str): The exception message. Defaults to "Invalid token provided."
        """
        super().__init__(message)


class NotFoundError(PollingError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Requested resource not found.") -> None:
        """Initialize the exception.

        Args:
            message (str): The exception message. Defaults to "Requested resource not found."
        """
        super().__init__(message)
