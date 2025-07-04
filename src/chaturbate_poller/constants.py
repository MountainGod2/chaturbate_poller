"""Constants for the chaturbate_poller module."""

from __future__ import annotations

import enum

# API Configuration
DEFAULT_BASE_URL = "https://eventsapi.chaturbate.com/events/{username}/{token}/"
TESTBED_BASE_URL = "https://eventsapi.testbed.cb.dev/events/{username}/{token}/"
API_TIMEOUT = 10

# Retry Configuration
MAX_RETRIES = 6
BACKOFF_BASE = 2.0
BACKOFF_FACTOR = 2.0
CONSTANT_INTERVAL = 10
READ_ERROR_MAX_TRIES = 5

# Logging Configuration
DEFAULT_CONSOLE_WIDTH = 100
MAX_TRACEBACK_FRAMES = 10

# HTTP Client Configuration
HTTP_CLIENT_TIMEOUT = 300


class HttpStatusCode(enum.IntEnum):
    """HTTP status codes used throughout the application."""

    # Success
    OK = 200
    NO_CONTENT = 204

    # Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404

    # Server Errors
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

    # Cloudflare Errors
    CLOUDFLARE_ERROR = 520
    WEB_SERVER_IS_DOWN = 521


EXAMPLE_JSON_STRING = """
{
    "events":[
        {
            "method":"mediaPurchase",
            "object":{
                "broadcaster": "example_broadcaster",
                "user": {
                    "username": "example_user",
                    "inFanclub": false,
                    "gender": "m",
                    "hasTokens": true,
                    "recentTips": "none",
                    "isMod": false
                },
                "media": {
                    "id": 1,
                    "name": "photoset1",
                    "type": "photos",
                    "tokens": 25
                }
            },
            "id":"UNIQUE_EVENT_ID"
        }
    ],
    "nextUrl":"https://eventsapi.chaturbate.com/events/REDACTED_BROADCASTER/REDACTED_API_TOKEN/?i=UNIQUE_EVENT_ID&timeout=10"
}
"""
