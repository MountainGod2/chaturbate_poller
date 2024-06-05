# src/chaturbate_event_listener/config.py
"""Configuration file for the Chaturbate event listener."""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access environment variables
CHATURBATE_USERNAME = os.getenv("CHATURBATE_USERNAME", "")
CHATURBATE_TOKEN = os.getenv("CHATURBATE_TOKEN", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
