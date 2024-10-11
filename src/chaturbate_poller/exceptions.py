"""Exceptions for the Chaturbate Poller."""


class PollingError(Exception):
    """Exception raised when there is an error during polling."""

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message (str): The exception message.
        """
        super().__init__(message)
