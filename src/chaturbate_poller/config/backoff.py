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
        self._max_tries: int = MAX_RETRIES
        self._read_error_max_tries: int = READ_ERROR_MAX_TRIES
        self._base: float = BACKOFF_BASE
        self._factor: float = BACKOFF_FACTOR
        self._constant_interval: int = CONSTANT_INTERVAL

    def enable(self) -> None:
        """Enable backoff retry logic."""
        self.enabled = True

    def disable_for_tests(self) -> None:
        """Disable backoff retry logic for testing."""
        self.enabled = False

    @property
    def max_tries(self) -> int:
        """Get the maximum number of retry attempts."""
        return 1 if not self.enabled else self._max_tries

    @max_tries.setter
    def max_tries(self, value: int) -> None:
        """Set the maximum number of retry attempts."""
        self._max_tries = value

    @property
    def read_error_max_tries(self) -> int:
        """Get the maximum tries for read errors."""
        return 1 if not self.enabled else self._read_error_max_tries

    @read_error_max_tries.setter
    def read_error_max_tries(self, value: int) -> None:
        """Set the maximum tries for read errors."""
        self._read_error_max_tries = value

    @property
    def base(self) -> float:
        """Get the backoff base value."""
        return 1 if not self.enabled else self._base

    @base.setter
    def base(self, value: float) -> None:
        """Set the backoff base value."""
        self._base = value

    @property
    def factor(self) -> float:
        """Get the backoff factor."""
        return 0 if not self.enabled else self._factor

    @factor.setter
    def factor(self, value: float) -> None:
        """Set the backoff factor."""
        self._factor = value

    @property
    def constant_interval(self) -> int:
        """Get the constant interval for retries."""
        return 0 if not self.enabled else self._constant_interval

    @constant_interval.setter
    def constant_interval(self, value: int) -> None:
        """Set the constant interval for retries."""
        self._constant_interval = value
