"""Backoff configuration for runtime control."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Self


class BackoffConfig:
    """Configuration class for backoff behavior."""

    _instance: BackoffConfig | None = None

    def __new__(cls) -> Self:
        """Singleton pattern to ensure single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cast("Self", cls._instance)

    def __init__(self) -> None:
        """Initialize backoff configuration."""
        if not hasattr(self, "_initialized"):
            self.enabled: bool = True
            self.max_tries: int = 6
            self.base: int = 2
            self.factor: int = 5
            self.constant_interval: int = 2
            self.read_error_max_tries: int = 10
            self._initialized: bool = True

    def disable_for_tests(self) -> None:
        """Disable backoff for testing (immediate retry with max_tries=1)."""
        self.enabled = False
        self.max_tries = 1
        self.read_error_max_tries = 1

    def enable(self) -> None:
        """Enable normal backoff behavior."""
        self.enabled = True
        self.max_tries = 6
        self.read_error_max_tries = 10

    def get_max_tries(self) -> int:
        """Get max tries for HTTP status errors."""
        return self.max_tries

    def get_read_error_max_tries(self) -> int:
        """Get max tries for read errors."""
        return self.read_error_max_tries

    def get_base(self) -> int:
        """Get exponential backoff base."""
        return self.base if self.enabled else 1

    def get_factor(self) -> int:
        """Get exponential backoff factor."""
        return self.factor if self.enabled else 0

    def get_constant_interval(self) -> int:
        """Get constant backoff interval."""
        return self.constant_interval if self.enabled else 0


# Global instance
backoff_config = BackoffConfig()
