"""Logging configuration for the chaturbate_poller package."""

from __future__ import annotations

import datetime
import json
import logging
import logging.config
import re
import sys

import rich.traceback

from chaturbate_poller.constants import DEFAULT_CONSOLE_WIDTH, MAX_TRACEBACK_FRAMES

URL_REGEX: re.Pattern[str] = re.compile(r"events/([^/]+)/([^/]+)")
"""re.Pattern[str]: Regular expression to match URLs with usernames and tokens."""
TOKEN_REGEX: re.Pattern[str] = re.compile(r"token=[^&]+")
"""re.Pattern[str]: Regular expression to match tokens."""

timezone_name: datetime.tzinfo | None = datetime.datetime.now().astimezone().tzinfo
"""tzinfo | None: The timezone name for log timestamps."""


def sanitize_sensitive_data(arg: str | float) -> str | float:
    """Sanitize sensitive data like URLs and tokens.

    Args:
        arg (str | float): The argument to sanitize.

    Returns:
        str | float: Sanitized data.
    """
    if isinstance(arg, str):
        arg = URL_REGEX.sub(r"events/USERNAME/TOKEN", arg)
        arg = TOKEN_REGEX.sub("token=REDACTED", arg)
    return arg


class SanitizeSensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive data from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data in log messages and arguments.

        Args:
            record: The log record.

        Returns:
            Whether to process the log.
        """
        if isinstance(record.msg, str):
            record.msg = sanitize_sensitive_data(arg=record.msg)
        if record.args:
            record.args = tuple(sanitize_sensitive_data(arg=str(arg)) for arg in record.args)
        return True


class CustomJSONFormatter(logging.Formatter):
    """Custom JSON Formatter for structured logging."""

    EXCLUDED_FIELDS: frozenset[str] = frozenset({
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
    })

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON.

        Args:
            record: The log record.

        Returns:
            JSON formatted log entry.
        """
        log_data: dict[str, object] = {
            "message": record.getMessage(),
            "level": record.levelname,
            "name": record.name,
            "time": datetime.datetime.fromtimestamp(
                timestamp=record.created, tz=timezone_name
            ).strftime(format="%Y-%m-%d %H:%M:%S"),
        }

        # Add extra fields that aren't in the excluded set
        if hasattr(record, "__dict__"):
            extras: dict[str, object] = {
                key: value
                for key, value in record.__dict__.items()
                if key not in self.EXCLUDED_FIELDS
            }
            log_data.update(extras)

        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(obj=log_data)


def _get_rich_handler_config() -> dict[str, object]:
    """Get configuration for RichHandler."""
    return {
        "rich_tracebacks": True,
        "tracebacks_show_locals": False,
        "tracebacks_width": DEFAULT_CONSOLE_WIDTH,
        "tracebacks_max_frames": MAX_TRACEBACK_FRAMES,
        "tracebacks_word_wrap": False,
        "tracebacks_theme": "monokai",
        "tracebacks_suppress": ["click", "rich_click"],
        "show_time": True,
        "show_path": True,
        "markup": True,
    }


def _get_console_handler_config(*, json_logging: bool, verbose: bool) -> dict[str, object]:
    """Get configuration for console handler."""
    config: dict[str, object] = {
        "class": "logging.StreamHandler" if json_logging else "rich.logging.RichHandler",
        "formatter": "json" if json_logging else "simple",
        "filters": ["sanitize"],
        "level": "DEBUG" if verbose else "INFO",
    }

    if not json_logging:
        config.update(_get_rich_handler_config())

    return config


def setup_logging(*, verbose: bool = False) -> None:
    """Set up logging configuration."""
    json_logging = not sys.stdout.isatty()

    if sys.stdout.isatty():
        rich.traceback.install()

    log_format = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sanitize": {"()": SanitizeSensitiveDataFilter},
        },
        "handlers": {
            "console": _get_console_handler_config(json_logging=json_logging, verbose=verbose),
        },
        "formatters": {
            "simple": {
                "format": "%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {"()": CustomJSONFormatter},
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
    logging.config.dictConfig(config=log_format)
