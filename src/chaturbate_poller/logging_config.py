"""Logging configuration for the Chaturbate poller."""

import logging

CRITICAL_LEVEL = 50
"""int: Custom level for CRITICAL events."""
logging.addLevelName(CRITICAL_LEVEL, "CRITICAL")
"""str: Name for the custom CRITICAL level."""


class CustomFormatter(logging.Formatter):
    """Custom formatter for including module and function names."""

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        """Format the log record."""
        record.module = record.module.split(".")[-1]
        record.funcName = record.funcName or ""
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "()": CustomFormatter,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s",  # noqa: E501
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "app.log",
            "formatter": "detailed",
            "level": "DEBUG",
            "when": "midnight",
            "backupCount": 7,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "chaturbate_poller": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
        "httpx": {
            "handlers": ["file"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "httpcore": {
            "handlers": ["file"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "backoff": {
            "handlers": ["file"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}
"""dict: Logging configuration for the Chaturbate poller."""
