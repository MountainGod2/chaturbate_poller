"""Utility functions for the Chaturbate poller."""

import logging

import httpx
from backoff._typing import Details

from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.exceptions import PollingError

logger = logging.getLogger(__name__)
"""logging.Logger: The module-level logger."""


class ChaturbateUtils:
    """Utility functions for the Chaturbate poller."""

    @staticmethod
    def backoff_handler(details: Details) -> None:
        """Handle backoff events.

        Args:
            details (Details): The backoff details.
        """
        wait = int(details["wait"])
        tries = int(details["tries"])
        logger.info("Backing off %s seconds after %s tries", wait, tries)

    @staticmethod
    def giveup_handler(details: Details) -> None:
        """Handle giveup events.

        Args:
            details (Details): The giveup details.
        """
        tries = int(details.get("tries", 0))
        exception = details.get("exception")
        response = getattr(exception, "response", None)
        status_code = response.status_code if response else None

        logger.error(
            "Giving up after %s tries due to server error: Status code %s", tries, status_code
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

    @staticmethod
    def need_retry(exception: Exception) -> bool:
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
