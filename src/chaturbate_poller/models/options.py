"""Data transfer object for CLI parameters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PollerOptions:
    """Configuration options for the Chaturbate Poller."""

    username: str
    token: str
    timeout: int
    testbed: bool = False
    use_database: bool = False
    verbose: bool = False

    def __post_init__(self) -> None:
        """Validate the options after initialization."""
        if not self.username or not self.token:
            msg = "Username and token are required"
            raise ValueError(msg)
        if self.timeout < 0:
            msg = "Timeout must be a positive integer"
            raise ValueError(msg)
