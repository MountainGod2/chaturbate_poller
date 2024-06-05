# src/chaturbate_event_listener/logger.py
"""Logging module for the chaturbate_event_listener package."""

import logging

from chaturbate_event_listener.config import LOG_LEVEL

logger = logging.getLogger("chaturbate_event_logger")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(
    "chaturbate_event_listener.log",
    mode="w",
    delay=True,
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.debug("Logger set up successfully.")
