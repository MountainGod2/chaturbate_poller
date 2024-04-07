"""Logging configuration for the Chaturbate poller."""

import datetime
import logging

# Define a custom level for CRITICAL events
CRITICAL_LEVEL = 50
logging.addLevelName(CRITICAL_LEVEL, "CRITICAL")


# Custom formatter for including module and function names
class CustomFormatter(logging.Formatter):
    """Custom formatter for including module and function names."""

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        """Format the log record."""
        record.module = record.module.split(".")[-1]  # Extract only module name
        record.funcName = record.funcName or ""  # Avoid NoneType error
        return super().format(record)


# Get current timestamp
current_timestamp = datetime.datetime.now(tz=datetime.timezone.utc).strftime(
    "%Y-%m-%d_%H-%M-%S"
)

# Logging configuration dictionary
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "()": CustomFormatter,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",  # noqa: E501
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
            "filename": f"app_{current_timestamp}.log",
            "formatter": "detailed",
            "level": "DEBUG",
            "when": "midnight",  # Rotate logs at midnight
            "backupCount": 7,  # Keep 7 backup log files
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "chaturbate_poller": {
            "handlers": ["file"],  # No need for console output
            "level": "INFO",
            "propagate": False,
        },
        "httpx": {
            "handlers": ["file"],  # No need for console output
            "level": "ERROR",
            "propagate": False,
        },
        "httpcore": {
            "handlers": ["file"],  # No need for console output
            "level": "ERROR",
            "propagate": False,
        },
        "backoff": {
            "handlers": ["file"],  # No need for console output
            "level": "ERROR",
            "propagate": False,
        },
    },
}
