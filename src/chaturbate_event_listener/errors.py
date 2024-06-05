"""Exceptions for Chaturbate Event Listener."""


class ChaturbateEventListenerError(Exception):
    """Base exception for Chaturbate Event Listener."""


class UnauthorizedError(ChaturbateEventListenerError):
    """Exception for unauthorized access."""


class ForbiddenError(ChaturbateEventListenerError):
    """Exception for forbidden access."""


class NotFoundError(ChaturbateEventListenerError):
    """Exception for resource not found."""
