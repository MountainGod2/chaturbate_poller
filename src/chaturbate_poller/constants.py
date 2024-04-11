"""Constants for the chaturbate_poller module."""

from enum import IntEnum

BASE_URL = "https://events.testbed.cb.dev/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events."""


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


API_TIMEOUT = 10
"""int: Maximum time in seconds that the server will wait before sending the nextURL."""

TIMEOUT_BUFFER = 5
"""int: Buffer time in seconds to add to the API timeout to prevent HTTP timeouts."""

RETRY_DELAY = 20
"""int: Delay in seconds before retrying the request."""
