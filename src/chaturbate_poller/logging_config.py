"""Logging configuration for the chaturbate_poller package."""

import json
import logging
import logging.config
import re
import sys
from datetime import datetime

from dateutil import tz
from rich.traceback import install as install_rich_traceback

# Regular expression to match Chaturbate event URLs and tokens
URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")
TOKEN_REGEX = re.compile(r"token=[^&]+")

# Timezone setup for log timestamps
timezone_name = tz.gettz("America/Edmonton")


def sanitize_sensitive_data(arg: str | float) -> str | int | float:
    """Sanitize sensitive data like URLs and tokens.

    Args:
        arg (str | float): The argument to sanitize.

    Returns:
        str | int | float: Sanitized data.
    """
    if isinstance(arg, str):
        arg = URL_REGEX.sub(r"events/USERNAME/TOKEN", arg)
        arg = TOKEN_REGEX.sub("token=REDACTED", arg)
    return arg


class SanitizeSensitiveDataFilter(logging.Filter):  # pylint: disable=R0903
    """Filter to sanitize sensitive data from logs."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: PLR6301, RUF100
        """Sanitize sensitive data in log messages and arguments.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            bool: Whether to process the log.
        """
        if isinstance(record.msg, str):
            record.msg = sanitize_sensitive_data(record.msg)
        if record.args:
            record.args = tuple(sanitize_sensitive_data(str(arg)) for arg in record.args)
        return True


class CustomJSONFormatter(logging.Formatter):
    """Custom JSON Formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: JSON formatted log entry.
        """
        log_data = {
            "message": record.getMessage(),
            "level": record.levelname,
            "name": record.name,
            "time": datetime.fromtimestamp(record.created, tz=timezone_name).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        if hasattr(record, "__dict__"):  # pragma: no branch
            extras = {
                key: value
                for key, value in record.__dict__.items()
                if key
                not in {
                    "msg",
                    "args",
                    "exc_info",
                    "levelname",
                    "pathname",
                    "lineno",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "funcName",
                    "name",
                }
            }
            log_data.update(extras)

        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(*, verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose (bool): Enable verbose logging (DEBUG level).
    """
    json_logging = not sys.stdout.isatty()  # JSON logging for non-TTY output

    if sys.stdout.isatty():
        install_rich_traceback()

    log_format = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sanitize": {
                "()": SanitizeSensitiveDataFilter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler" if json_logging else "rich.logging.RichHandler",
                "formatter": "json" if json_logging else "simple",
                "filters": ["sanitize"],
                "level": "DEBUG" if verbose else "INFO",
                **(
                    {}
                    if json_logging
                    else {
                        "rich_tracebacks": True,
                        "tracebacks_show_locals": True,
                        "show_time": True,
                        "show_path": True,
                    }
                ),
            },
        },
        "formatters": {
            "simple": {
                "format": "%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": CustomJSONFormatter,
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
