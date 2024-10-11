"""Utility functions for the Chaturbate poller."""

import logging

import httpx
from backoff._typing import Details

from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.exceptions import PollingError

logger = logging.getLogger(__name__)


class ChaturbateUtils:
    """Utility functions for the Chaturbate poller."""

    def __init__(self) -> None:
        """Initialize the utility class."""

    def backoff_handler(self, details: Details) -> None:
        """Handle backoff events.

        Args:
            details (Details): The backoff details.
        """
        wait = details["wait"]
        tries = details["tries"]
        logger.info("Backing off %s seconds after %s tries", int(wait), int(tries))

    def giveup_handler(self, details: Details) -> None:
        """Handle giveup events.

        Args:
            details (Details): The giveup details.
        """
        tries = details.get("tries", 0)
        exception = details.get("exception")

        if exception and hasattr(exception, "response"):
            response = exception.response
            status_code = response.status_code
        else:
            status_code = None

        logger.error(
            "Giving up after %s tries due to server error: Status code %s", int(tries), status_code
        )

        if status_code == HttpStatusCode.FORBIDDEN:
            msg = "Giving up due to invalid credentials"
            raise PollingError(msg)
        if status_code == HttpStatusCode.NOT_FOUND:
            msg = "Giving up due to invalid username"
            raise PollingError(msg)
        if status_code == HttpStatusCode.UNAUTHORIZED:
            msg = "Giving up due to invalid token"
            raise PollingError(msg)

        msg = "Giving up due to unhandled polling error"
        raise PollingError(msg)

    def need_retry(self, exception: Exception) -> bool:
        """Determine if the request should be retried based on the exception.

        Args:
            exception (Exception): The exception raised.

        Returns:
            bool: True if the request should be retried, False otherwise.
        """
        if isinstance(exception, httpx.HTTPStatusError):
            status_code = exception.response.status_code
            if status_code in {
                HttpStatusCode.INTERNAL_SERVER_ERROR,
                HttpStatusCode.BAD_GATEWAY,
                HttpStatusCode.SERVICE_UNAVAILABLE,
                HttpStatusCode.GATEWAY_TIMEOUT,
                HttpStatusCode.WEB_SERVER_IS_DOWN,
            }:
                return True
        return False
