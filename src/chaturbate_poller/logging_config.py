"""Logging configuration for the chaturbate_poller package."""

import logging
import logging.config
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from dateutil import tz
from json_log_formatter import JSONFormatter

# Regular expression to match Chaturbate event URLs and tokens
URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")
TOKEN_REGEX = re.compile(r"token=[^&]+")

timezone_name = tz.gettz(os.getenv("TZ", "America/Edmonton"))
log_timestamp = datetime.now(tz=timezone_name).strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"logs/{log_timestamp}.log"  # Convert to string for compatibility


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


class CustomFormatter(logging.Formatter):
    """Custom log formatter for detailed logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: The formatted log record.
        """
        record.module = record.module.split(".")[-1]  # Simplify module name
        return super().format(record)


LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": CustomFormatter,  # Use CustomFormatter
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": CustomJSONFormatter,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "sanitize_sensitive_data": {
            "()": SanitizeSensitiveDataFilter,
        }
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "standard",  # CustomFormatter applied here
            "level": "INFO",
            "filters": ["sanitize_sensitive_data"],
            "rich_tracebacks": True,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_filename,
            "mode": "w",
            "encoding": "utf-8",
            "backupCount": 5,
            "maxBytes": 10485760,
            "formatter": "json",  # Use JSONFormatter for structured logs
            "level": "DEBUG",
            "filters": ["sanitize_sensitive_data"],
        },
    },
    "loggers": {
        "chaturbate_poller": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}


def setup_logging(*, verbose: bool = False) -> None:
    """Set up logging configuration and ensure log directory exists."""
    log_directory = Path("logs")
    try:
        if not log_directory.exists():
            log_directory.mkdir(parents=True, exist_ok=True)
        log_directory.chmod(0o750)  # Restrict permissions
    except PermissionError as e:  # pragma: no cover
        logging.critical(
            "Cannot create or access log directory '%s': %s", log_directory, e
        )  # pragma: no cover
        msg = f"Cannot create or access log directory '{log_directory}': {e}"  # pragma: no cover
        raise RuntimeError(msg) from e  # pragma: no cover

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.captureWarnings(capture=True)

    if verbose:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        logging.getLogger("chaturbate_poller").setLevel(logging.DEBUG)
