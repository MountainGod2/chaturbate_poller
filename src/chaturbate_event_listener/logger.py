"""Logging module for the chaturbate_event_listener package."""

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("chaturbate_event_listener")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(
    "chaturbate_event_listener.log", mode="w", maxBytes=0, backupCount=2, delay=False
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug("Logger set up successfully.")
