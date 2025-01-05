"""Constants for the chaturbate_poller module."""

from enum import IntEnum

DEFAULT_BASE_URL = "https://eventsapi.chaturbate.com/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events."""

TESTBED_BASE_URL = "https://events.testbed.cb.dev/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events in the test environment."""

API_TIMEOUT = 10
"""int: Maximum time in seconds that the server will wait before sending the nextURL."""

MAX_RETRIES = 6
"""int: Maximum number of retry attempts for polling."""


class HttpStatusCode(IntEnum):
    """HttpStatusCode is an enumeration of common HTTP status codes."""

    OK = 200
    """int: HTTP status code for OK (200)."""
    CREATED = 201
    """int: HTTP status code for CREATED (201)."""
    ACCEPTED = 202
    """int: HTTP status code for ACCEPTED (202)."""
    NO_CONTENT = 204
    """int: HTTP status code for NO_CONTENT (204)."""
    BAD_REQUEST = 400
    """int: HTTP status code for BAD_REQUEST (400)."""
    UNAUTHORIZED = 401
    """int: HTTP status code for UNAUTHORIZED (401)."""
    FORBIDDEN = 403
    """int: HTTP status code for FORBIDDEN (403)."""
    NOT_FOUND = 404
    """int: HTTP status code for NOT_FOUND (404)."""
    METHOD_NOT_ALLOWED = 405
    """int: HTTP status code for METHOD_NOT_ALLOWED (405)."""
    CONFLICT = 409
    """int: HTTP status code for CONFLICT (409)."""
    INTERNAL_SERVER_ERROR = 500
    """int: HTTP status code for INTERNAL_SERVER_ERROR (500)."""
    NOT_IMPLEMENTED = 501
    """int: HTTP status code for NOT_IMPLEMENTED (501)."""
    BAD_GATEWAY = 502
    """int: HTTP status code for BAD_GATEWAY (502)."""
    SERVICE_UNAVAILABLE = 503
    """int: HTTP status code for SERVICE_UNAVAILABLE (503)."""
    GATEWAY_TIMEOUT = 504
    """int: HTTP status code for GATEWAY_TIMEOUT (504)."""
    CLOUDFLARE_ERROR = 520
    """int: HTTP status code for CLOUDFLARE_ERROR (520)."""
    WEB_SERVER_IS_DOWN = 521
    """int: HTTP status code for WEB_SERVER_IS_DOWN (521)."""


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
"""str: An example JSON string representing the EventsAPIResponse object."""
