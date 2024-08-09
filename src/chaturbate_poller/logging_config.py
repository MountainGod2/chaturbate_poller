"""Logging configuration for the application."""

import logging
import logging.handlers
import re

URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")


def sanitize_url(url: str) -> str:
    """Sanitize the URL by replacing username and token with placeholders."""
    return URL_REGEX.sub(r"events/USERNAME/TOKEN", url)


class SanitizeURLFilter(logging.Filter):
    """Logging filter to sanitize sensitive information from URLs.

    Args:
        logging.Filter: The logging filter class.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to sanitize URLs."""
        if isinstance(record.msg, str):
            record.msg = sanitize_url(record.msg)
        if record.args:
            record.args = tuple(sanitize_url(str(arg)) for arg in record.args)
        return True

    def __repr__(self) -> str:
        """Return a string representation of the filter."""
        return f"{self.__class__.__name__}()"


class CustomFormatter(logging.Formatter):
    """Custom log formatter.

    Args:
        logging.Formatter: The logging formatter class.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record.
        """
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
            "filters": ["sanitize_url"],  # Add filter here
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "app.log",
            "formatter": "detailed",
            "level": "DEBUG",
            "when": "midnight",
            "filters": ["sanitize_url"],  # Add filter here
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
