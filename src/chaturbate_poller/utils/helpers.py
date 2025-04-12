"""Utility functions for the Chaturbate poller."""

from __future__ import annotations

import logging
from logging import Logger
from typing import TYPE_CHECKING

import httpx

from chaturbate_poller.constants import MAX_RETRIES, HttpStatusCode
from chaturbate_poller.exceptions import PollingError

if TYPE_CHECKING:
    from backoff._typing import Details  # basedpyright: ignore[disable=reportPrivateImportUsage]

logger: Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""


class ChaturbateUtils:
    """Utility functions for the Chaturbate poller."""

    @staticmethod
    def get_max_tries() -> int:
        """Get the maximum number of retry attempts for polling.

        Returns:
            int: The maximum number of retry attempts.
        """
        return MAX_RETRIES

    @staticmethod
    def backoff_handler(details: Details) -> None:
        """Log backoff events during retries.

        Args:
            details (Details): The backoff details.
        """
        wait = int(details.get("wait", 0))
        tries = int(details.get("tries", 0))
        logger.warning("Backing off for %s seconds after %s tries.", wait, tries)

    @staticmethod
    def giveup_handler(details: Details) -> None:
        """Handle the give-up scenario after retry attempts.

        Args:
            details (Details): The give-up details.

        Raises:
            PollingError: An appropriate error based on the HTTP status code.
        """
        tries = int(details.get("tries", 0))
        exception = details.get("exception")
        response = getattr(exception, "response", None)
        status_code = response.status_code if response else None

        logger.error(
            "Giving up after %s tries. Last error: %s. Status code: %s",
            tries,
            exception,
            status_code,
        )

        if status_code == HttpStatusCode.FORBIDDEN:
            msg = "Access forbidden. Check credentials."
            raise PollingError(msg)
        if status_code == HttpStatusCode.NOT_FOUND:
            msg = "Resource not found."
            raise PollingError(msg)
        if status_code == HttpStatusCode.UNAUTHORIZED:
            msg = "Invalid token or unauthorized access."
            raise PollingError(msg)

        msg = "Unhandled polling error encountered."
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
            logger.debug("Retrying for status code: %s", status_code)
            if status_code in {
                HttpStatusCode.INTERNAL_SERVER_ERROR,
                HttpStatusCode.BAD_GATEWAY,
                HttpStatusCode.SERVICE_UNAVAILABLE,
                HttpStatusCode.GATEWAY_TIMEOUT,
                HttpStatusCode.CLOUDFLARE_ERROR,
                HttpStatusCode.WEB_SERVER_IS_DOWN,
            }:
                return True
        return False
