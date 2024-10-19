"""Logging configuration for the chaturbate_poller package."""

import logging
import logging.config
import re
import uuid
from pathlib import Path
from typing import Any

from json_log_formatter import JSONFormatter

# Regular expression to match Chaturbate event URLs and tokens
URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")
"""str: Regular expression to match Chaturbate event URLs and tokens."""
TOKEN_REGEX = re.compile(r"token=[^&]+")
"""str: Regular expression to match Chaturbate API tokens."""


def sanitize_sensitive_data(arg: str | float) -> str | int | float:
    """Sanitize sensitive data like URLs and tokens."""
    if isinstance(arg, str):
        arg = URL_REGEX.sub(r"events/USERNAME/TOKEN", arg)
        arg = TOKEN_REGEX.sub("token=REDACTED", arg)
    return arg


class SanitizeSensitiveDataFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Filter to sanitize sensitive data from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data from log records.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            bool: True if the record should be logged, False otherwise.
        """
        if isinstance(record.msg, str):
            record.msg = sanitize_sensitive_data(record.msg)
        if record.args:
            record.args = tuple(sanitize_sensitive_data(str(arg)) for arg in record.args)
        return True


class AddCorrelationIDFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Filter to add correlation ID to logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log records.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            bool: True if the record should be logged, False otherwise.
        """
        if not hasattr(record, "correlation_id"):
            record.correlation_id = uuid.uuid4()  # Add unique ID to the log record
        return True


class CustomJSONFormatter(JSONFormatter):
    """Custom JSON Formatter for structured logging."""

    def json_record(
        self,
        message: str,
        extra: dict[str, Any],
        record: logging.LogRecord,
    ) -> dict[str, Any]:
        """Format the log record as a JSON object.

        Args:
            message (str): The log message.
            extra (dict): Extra attributes to include in the log record.
            record (logging.LogRecord): The log record.

        Returns:
            dict: The formatted log record.
        """
        extra["message"] = message
        extra["level"] = record.levelname
        extra["name"] = record.name
        extra["time"] = self.formatTime(record, self.datefmt)
        extra["correlation_id"] = getattr(record, "correlation_id", "N/A")
        return extra


class CustomFormatter(logging.Formatter):
    """Custom log formatter for detailed logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: The formatted log record.
        """
        record.module = record.module.split(".")[-1]
        record.correlation_id = getattr(record, "correlation_id", "N/A")
        return super().format(record)


LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": CustomJSONFormatter,
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "sanitize_sensitive_data": {
            "()": SanitizeSensitiveDataFilter,
        },
        "add_correlation_id": {
            "()": AddCorrelationIDFilter,
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "standard",
            "level": "INFO",
            "filters": ["sanitize_sensitive_data"],
            "rich_tracebacks": True,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/chaturbate_poller.log",
            "mode": "w",
            "encoding": "utf-8",
            "backupCount": 5,
            "maxBytes": 10485760,  # 10 MB
            "formatter": "json",  # Use JSON formatter for file logs
            "level": "DEBUG",
            "filters": ["sanitize_sensitive_data", "add_correlation_id"],
        },
    },
    "loggers": {
        "chaturbate_poller": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}
"""dict: Logging configuration for the chaturbate_poller package."""

def setup_logging() -> None:
    """Set up logging configuration and ensure log directory exists."""
    log_directory = Path("logs")
    if not log_directory.exists():
        log_directory.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.captureWarnings(capture=True)
