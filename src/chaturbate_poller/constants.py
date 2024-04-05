"""Constants for the chaturbate_poller module."""

BASE_URL = "https://events.testbed.cb.dev/events/{username}/{token}/"
"""str: The base URL for fetching Chaturbate events."""

ERROR_RANGE_START = 500
"""int: Start of the range of HTTP status codes that are considered errors."""

ERROR_RANGE_END = 600
"""int: End of the range of HTTP status codes that are considered errors."""

API_TIMEOUT = 10
"""int: Maximum time in seconds that the server will wait before sending the nextURL."""

TIMEOUT_BUFFER = 5
"""int: Buffer time in seconds to add to the API timeout to prevent HTTP timeouts."""

RETRY_DELAY = 20
"""int: Delay in seconds before retrying the request."""
