# chaturbate_poller/src/chaturbate_poller/logging_config.py
"""Logging configuration for the application."""

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "standard",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "chaturbate_poller": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "httpx": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "httpcore": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "backoff": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
"""Logging configuration for the application."""
