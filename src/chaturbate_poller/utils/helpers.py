"""Utility functions for the Chaturbate poller."""

from __future__ import annotations

import logging

import httpx

from chaturbate_poller.constants import MAX_RETRIES, HttpStatusCode

logger = logging.getLogger(__name__)


def get_max_tries() -> int:
    """Get the maximum number of retry attempts for polling."""
    return MAX_RETRIES


def need_retry(exception: Exception) -> bool:
    """Determine if the request should be retried based on the exception."""
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
