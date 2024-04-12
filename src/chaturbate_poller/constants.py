"""Constants for the chaturbate_poller module."""

from enum import IntEnum

BASE_URL = "https://eventsapi.chaturbate.com/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events."""

TESTBED_BASE_URL = "https://events.testbed.cb.dev/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events in the test environment."""


class HttpStatusCode(IntEnum):
    """HTTP status codes."""

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    WEB_SERVER_IS_DOWN = 521


API_TIMEOUT = 10
"""int: Maximum time in seconds that the server will wait before sending the nextURL."""

TIMEOUT_BUFFER = 5
"""int: Buffer time in seconds to add to the API timeout to prevent HTTP timeouts."""

RETRY_DELAY = 20
"""int: Delay in seconds before retrying the request."""

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
"""str: A JSON string representing the EventsAPIResponse object."""
