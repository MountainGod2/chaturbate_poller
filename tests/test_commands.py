from collections.abc import Generator
from typing import Any
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from click.testing import CliRunner

from chaturbate_poller.cli.commands import cli
from chaturbate_poller.exceptions import PollingError


@pytest.fixture
def mock_main() -> Generator[MagicMock | AsyncMock, Any]:  # pyright: ignore[reportExplicitAny]
    """Mock the main function in the CLI module."""
    with mock.patch("chaturbate_poller.cli.commands.main", autospec=True) as mocked_main:
        yield mocked_main


@pytest.fixture
def mock_logger() -> Generator[MagicMock | AsyncMock, Any]:  # pyright: ignore[reportExplicitAny]
    """Mock the logger in the CLI module."""
    with mock.patch("chaturbate_poller.cli.commands.logger", autospec=True) as mocked_logger:
        yield mocked_logger


@pytest.fixture
def mock_sys_exit() -> Generator[MagicMock | AsyncMock, Any]:  # pyright: ignore[reportExplicitAny]
    """Mock sys.exit to prevent the script from exiting."""
    with mock.patch("sys.exit", autospec=True) as mocked_exit:
        yield mocked_exit


def test_start_success(mock_main: MagicMock) -> None:
    """Test the `start` command when it runs successfully."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "start",
            "--username",
            "test_user",
            "--token",
            "test_token",
            "--timeout",
            "10",
            "--database",
            "--verbose",
        ],
    )

    assert result.exit_code == 0
    mock_main.assert_called_once_with(
        username="test_user",
        token="test_token",  # noqa: S106
        api_timeout=10,
        testbed=False,
        use_database=True,
        verbose=True,
    )


def test_start_polling_error(
    mock_main: MagicMock, mock_logger: MagicMock, mock_sys_exit: MagicMock
) -> None:
    """Test the `start` command when a PollingError is raised."""
    mock_main.side_effect = PollingError("Polling failed")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "start",
            "--username",
            "test_user",
            "--token",
            "test_token",
            "--timeout",
            "10",
        ],
    )

    mock_main.assert_called_once()
    mock_logger.exception.assert_called_once_with("Polling error encountered. Exiting.")
    mock_sys_exit.assert_any_call(1)
    assert mock_sys_exit.call_count == 2


def test_start_invalid_arguments() -> None:
    """Test the `start` command with invalid arguments."""
    runner = CliRunner()
    result = runner.invoke(cli, ["start", "--timeout", "-1"])

    assert result.exit_code != 0
    assert "Timeout must be a positive integer" in result.output
