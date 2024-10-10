"""Exceptions for the Chaturbate Poller."""


class RetryError(Exception):
    """Exception raised when the request should be retried."""

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message (str): The exception message.
        """
        super().__init__(message)
