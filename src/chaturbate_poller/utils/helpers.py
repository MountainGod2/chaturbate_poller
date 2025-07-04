"""Utility functions for the Chaturbate poller."""

from __future__ import annotations

import logging

import httpx

from chaturbate_poller.constants import HttpStatusCode

logger = logging.getLogger(__name__)

# Define retryable status codes as a constant
RETRYABLE_STATUS_CODES = frozenset({
    HttpStatusCode.INTERNAL_SERVER_ERROR,
    HttpStatusCode.BAD_GATEWAY,
    HttpStatusCode.SERVICE_UNAVAILABLE,
    HttpStatusCode.GATEWAY_TIMEOUT,
    HttpStatusCode.CLOUDFLARE_ERROR,
    HttpStatusCode.WEB_SERVER_IS_DOWN,
})


def need_retry(exception: Exception) -> bool:
    """Determine if the request should be retried based on the exception.

    Args:
        exception: The exception to check.

    Returns:
        True if the request should be retried, False otherwise.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code
        logger.debug("Checking retry for status code: %s", status_code)
        return status_code in RETRYABLE_STATUS_CODES
    return False
