"""Constants for the chaturbate_poller module."""

from enum import IntEnum

DEFAULT_BASE_URL = "https://eventsapi.chaturbate.com/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events."""

TESTBED_BASE_URL = "https://events.testbed.cb.dev/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events in the test environment."""


class HttpStatusCode(IntEnum):
    """HttpStatusCode is an enumeration of common HTTP status codes.

    Attributes:
        OK (int): Standard response for successful HTTP requests.
        CREATED (int): The request has been fulfilled, resulting in the creation of a new resource.
        ACCEPTED (int): The request has been accepted for processing, but the processing has not
            been completed.
        NO_CONTENT (int): The server successfully processed the request, but is not returning any
            content.
        BAD_REQUEST (int): The server cannot or will not process the request due to an apparent
            client error.
        UNAUTHORIZED (int): Authentication is required and has failed or has not yet been provided.
        FORBIDDEN (int): The request was valid, but the server is refusing action.
        NOT_FOUND (int): The requested resource could not be found but may be available in the
            future.
        METHOD_NOT_ALLOWED (int): A request method is not supported for the requested resource.
        CONFLICT (int): The request could not be processed because of conflict in the request.
        INTERNAL_SERVER_ERROR (int): A generic error message, given when an unexpected condition
            was encountered.
        NOT_IMPLEMENTED (int): The server either does not recognize the request method, or it lacks
            the ability to fulfill the request.
        BAD_GATEWAY (int): The server was acting as a gateway or proxy and received an invalid
            response from the upstream server.
        SERVICE_UNAVAILABLE (int): The server is currently unavailable (because it is overloaded or
            down for maintenance).
        GATEWAY_TIMEOUT (int): The server was acting as a gateway or proxy and did not receive a
            timely response from the upstream server.
        WEB_SERVER_IS_DOWN (int): The web server is down.
    """

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
"""str: An example JSON string representing the EventsAPIResponse object."""
