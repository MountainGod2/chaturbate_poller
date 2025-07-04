"""Error handling utilities for the Chaturbate Poller."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.exceptions import PollingError

if TYPE_CHECKING:
    from backoff._typing import Details

logger = logging.getLogger(__name__)


def handle_giveup(details: Details) -> None:
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

    error_messages = {
        HttpStatusCode.FORBIDDEN: "Access forbidden. Check credentials.",
        HttpStatusCode.NOT_FOUND: "Resource not found.",
        HttpStatusCode.UNAUTHORIZED: "Invalid token or unauthorized access.",
    }

    if status_code and status_code in error_messages:
        raise PollingError(error_messages[status_code])

    msg = "Unhandled polling error encountered."
    raise PollingError(msg)


def log_backoff(details: Details) -> None:
    """Log backoff events during retries.

    Args:
        details (Details): The backoff details.
    """
    wait = int(details.get("wait", 0))
    tries = int(details.get("tries", 0))
    logger.warning("Backing off for %s seconds after %s tries.", wait, tries)
