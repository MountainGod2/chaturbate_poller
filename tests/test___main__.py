# ruff: noqa: S101
"""Tests for the __main__ module."""

import asyncio
from contextlib import suppress

import pytest

from chaturbate_poller.__main__ import start_polling


def test_start_polling() -> None:
    """Test the start_polling function."""
    with (
        suppress(KeyboardInterrupt),
        pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."),
    ):
        asyncio.run(start_polling("username", "token", 10, testbed=False, verbose=False))
