"""Logging configuration for the chaturbate_poller package."""

import logging
import logging.handlers
import re

# Regular expression to match sensitive URL parts.
URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")


def sanitize_url(arg: str | float) -> str | int | float:
    """Sanitize URL if the argument is a string. Otherwise, return the argument as is.

    Args:
        arg (str | float): The argument to potentially sanitize.

    Returns:
        str | int | float: The sanitized URL or the original argument.
    """
    if isinstance(arg, str):
        return URL_REGEX.sub(r"events/USERNAME/TOKEN", arg)
    return arg


class SanitizeURLFilter(logging.Filter):  # pylint:disable=too-few-public-methods
    """Logging filter to sanitize sensitive information from URLs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to sanitize URLs."""
        if isinstance(record.msg, str):
            record.msg = sanitize_url(record.msg)
        if record.args:
            record.args = tuple(sanitize_url(str(arg)) for arg in record.args)
        return True


class CustomFormatter(logging.Formatter):
    """Custom log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        record.module = record.module.split(".")[-1]
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "()": CustomFormatter,
            "format": "%(asctime)s - %(levelname)s - %(module)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "sanitize_url": {
            "()": SanitizeURLFilter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "filters": ["sanitize_url"],
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "app.log",
            "backupCount": 7,
            "formatter": "detailed",
            "level": "DEBUG",
            "when": "midnight",
            "filters": ["sanitize_url"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "chaturbate_poller": {
            "level": "INFO",
        },
        "chaturbate_poller.chaturbate_client": {
            "level": "DEBUG",
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
        "_tracer": {
            "level": "WARNING",
        },
    },
}
