"""Logging configuration for the chaturbate_poller package."""

import logging
import logging.handlers
import re

URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")
"""str: Regular expression to match Chaturbate event URLs."""

TOKEN_REGEX = re.compile(r"token=[^&]+")
"""Regular expression to match API tokens in query parameters."""


def sanitize_sensitive_data(arg: str | float) -> str | int | float:
    """Sanitize sensitive data like URLs, tokens, or other sensitive fields."""
    if isinstance(arg, str):
        arg = URL_REGEX.sub(r"events/USERNAME/TOKEN", arg)  # Mask sensitive URLs
        arg = TOKEN_REGEX.sub("token=REDACTED", arg)  # Mask tokens
    return arg


class SanitizeSensitiveDataFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Logging filter to sanitize sensitive information from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to sanitize URLs and sensitive data."""
        if isinstance(record.msg, str):  # Add tests for this line
            record.msg = sanitize_sensitive_data(record.msg)  # Add tests for this line
        if record.args:  # Add tests for this line
            record.args = tuple(sanitize_sensitive_data(str(arg)) for arg in record.args)
        return True


class CustomFormatter(logging.Formatter):
    """Custom log formatter for detailed logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        record.module = record.module.split(".")[-1]  # Simplify module name in logs
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "()": CustomFormatter,  # Use custom formatter for detailed logs
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "sanitize_sensitive_data": {
            "()": SanitizeSensitiveDataFilter,  # Use the enhanced sanitization
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "filters": ["sanitize_sensitive_data"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/chaturbate_poller.log",
            "mode": "w",
            "encoding": "utf-8",
            "backupCount": 5,
            "maxBytes": 10485760,  # 10 MB
            "formatter": "detailed",
            "level": "DEBUG",
            "filters": ["sanitize_sensitive_data"],
        },
    },
    "loggers": {
        "chaturbate_poller": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "chaturbate_poller.chaturbate_client": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,  # Prevent double logging
        },
        "chaturbate_poller.event_handler": {
            "handlers": ["console", "file"],
            "level": "INFO",  # Adjust log levels based on needs
            "propagate": False,
        },
        "httpx": {
            "level": "WARNING",
        },
        "backoff": {
            "level": "WARNING",
        },
        "asyncio": {
            "level": "WARNING",
        },
    },
}
