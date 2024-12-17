"""Logging configuration for the chaturbate_poller package."""

import logging
import logging.config
import re
from typing import Any

from dateutil import tz
from json_log_formatter import JSONFormatter

# Regular expression to match Chaturbate event URLs and tokens
URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")
TOKEN_REGEX = re.compile(r"token=[^&]+")

# Timezone setup for log timestamps
timezone_name = tz.gettz("America/Edmonton")


def sanitize_sensitive_data(arg: str | float) -> str | int | float:
    """Sanitize sensitive data like URLs and tokens."""
    if isinstance(arg, str):
        arg = URL_REGEX.sub(r"events/USERNAME/TOKEN", arg)
        arg = TOKEN_REGEX.sub("token=REDACTED", arg)
    return arg


class SanitizeSensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive data from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data in log messages and arguments."""
        if isinstance(record.msg, str):
            record.msg = sanitize_sensitive_data(record.msg)
        if record.args:
            record.args = tuple(sanitize_sensitive_data(str(arg)) for arg in record.args)
        return True


class CustomJSONFormatter(JSONFormatter):
    """Custom JSON Formatter for structured logging."""

    def json_record(
        self, message: str, extra: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]:
        """Add extra fields to the JSON log record."""
        extra["message"] = message
        extra["level"] = record.levelname
        extra["name"] = record.name
        extra["time"] = self.formatTime(record, self.datefmt)
        return extra


def setup_logging(*, verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose (bool): Enable verbose logging (DEBUG level).
        json_output (bool): Force JSON output, overrides Docker detection.
    """
    log_format = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": "DEBUG" if verbose else "INFO",
            },
        },
        "formatters": {
            "simple": {
                "format": "[%(levelname)s] %(asctime)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": CustomJSONFormatter,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG" if verbose else "INFO",
        },
        "loggers": {
            "httpx": {"level": "WARNING"},
            "httpcore": {"level": "WARNING"},
            "asyncio": {"level": "WARNING"},
        },
    }
    logging.config.dictConfig(log_format)
