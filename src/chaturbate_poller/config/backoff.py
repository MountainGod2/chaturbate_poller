"""Backoff configuration for the Chaturbate Poller."""

from __future__ import annotations

from chaturbate_poller.constants import (
    BACKOFF_BASE,
    BACKOFF_FACTOR,
    CONSTANT_INTERVAL,
    MAX_RETRIES,
    READ_ERROR_MAX_TRIES,
)


class BackoffConfig:
    """Configuration class for backoff retry logic with testing support."""

    def __init__(self) -> None:
        """Initialize backoff configuration."""
        self.enabled: bool = True
        self.max_tries: int = MAX_RETRIES
        self.read_error_max_tries: int = READ_ERROR_MAX_TRIES
        self.base: float = BACKOFF_BASE
        self.factor: float = BACKOFF_FACTOR
        self.constant_interval: int = CONSTANT_INTERVAL

    def enable(self) -> None:
        """Enable backoff retry logic."""
        self.enabled = True
        self.max_tries = MAX_RETRIES
        self.read_error_max_tries = READ_ERROR_MAX_TRIES

    def disable_for_tests(self) -> None:
        """Disable backoff retry logic for testing."""
        self.enabled = False

    def get_max_tries(self) -> int:
        """Get the maximum number of retry attempts.

        Returns:
            int: Maximum retry attempts.
        """
        return 1 if not self.enabled else self.max_tries

    def get_read_error_max_tries(self) -> int:
        """Get the maximum tries for read errors.

        Returns:
            int: Maximum read error retry attempts.
        """
        return 1 if not self.enabled else self.read_error_max_tries

    def get_base(self) -> float:
        """Get the backoff base value.

        Returns:
            float: Base value for exponential backoff.
        """
        return 1 if not self.enabled else self.base

    def get_factor(self) -> float:
        """Get the backoff factor.

        Returns:
            float: Factor for exponential backoff calculation.
        """
        return 0 if not self.enabled else self.factor

    def get_constant_interval(self) -> int:
        """Get the constant interval for retries.

        Returns:
            int: Constant interval in seconds.
        """
        return 0 if not self.enabled else self.constant_interval
