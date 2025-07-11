"""Exceptions for the Chaturbate Poller."""

from __future__ import annotations


class PollingError(Exception):
    """Base exception for polling errors.

    This exception is raised for general polling errors, including
    authentication failures, resource not found errors, and client
    processing errors.
    """

    default_message: str = "Polling error occurred."

    def __init__(self, message: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message (str): The exception message.
        """
        super().__init__(message or self.default_message)


class AuthenticationError(PollingError):
    """Exception raised when there is an authentication failure."""

    default_message: str = "Invalid token provided."


class NotFoundError(PollingError):
    """Exception raised when a resource is not found."""

    default_message: str = "Requested resource not found."


class ClientProcessingError(PollingError):
    """Exception raised if an error occurs during processing."""

    default_message: str = "Error processing request."
