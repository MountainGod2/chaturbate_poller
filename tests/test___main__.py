# ruff: noqa: S101, S607, S603
"""Tests for the __main__ module."""

import asyncio
import subprocess
from contextlib import suppress

import pytest

from chaturbate_poller.__main__ import start_polling


def test_cli_missing_arguments() -> None:
    """Test the CLI with missing arguments."""
    result = subprocess.run(
        ["python", "-m", "chaturbate_poller", "--username", "testuser"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Unauthorized access. Verify the username and token" in result.stderr


def test_cli_with_invalid_token() -> None:
    """Test the CLI with an invalid token."""
    result = subprocess.run(
        ["python", "-m", "chaturbate_poller", "--username", "testuser", "--token", "invalid"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Unauthorized access" in result.stderr


def test_start_polling() -> None:
    """Test the start_polling function."""
    with (
        suppress(KeyboardInterrupt),
        pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."),
    ):
        asyncio.run(start_polling("username", "token", 10, testbed=False, verbose=False))
