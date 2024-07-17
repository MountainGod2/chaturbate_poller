"""This module contains custom exceptions for the Chaturbate Event Listener."""


class ServerError(Exception):
    """Exception raised for server errors."""


class EventPollerError(Exception):
    """Base class for exceptions in EventPoller."""


class UnauthorizedError(EventPollerError):
    """Exception raised for unauthorized errors."""


class EventParsingError(EventPollerError):
    """Exception raised when an event fails to parse."""
