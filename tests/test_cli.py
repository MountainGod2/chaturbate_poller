import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from chaturbate_poller.cli import cli
from chaturbate_poller.exceptions import PollingError


class TestCLI:
    """Tests for the CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for Click CLI runner.

        Returns:
            CliRunner: Click CLI runner.
        """
        return CliRunner()

    def test_cli_version(self, runner: CliRunner) -> None:
        """Test the CLI version command."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "chaturbate-poller, version" in result.output

    def test_cli_help(self, runner: CliRunner) -> None:
        """Test the CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Manage and run the Chaturbate Poller CLI" in result.output

    @patch("chaturbate_poller.cli.commands.ConfigManager")
    @patch("chaturbate_poller.cli.commands.main", new_callable=AsyncMock)
    def test_start_command_defaults(
        self, mock_main: AsyncMock, mock_config_manager: AsyncMock, runner: CliRunner
    ) -> None:
        """Test the `start` command with default options."""
        mock_config_manager.return_value.get.side_effect = lambda key, default=None: {
            "CB_USERNAME": "default_user",
            "CB_TOKEN": "default_token",
        }.get(key, default)

        result = runner.invoke(cli, ["start"])
        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            username="default_user",
            token="default_token",  # noqa: S106
            api_timeout=10,
            testbed=False,
            use_database=False,
            verbose=False,
        )

    @patch("chaturbate_poller.cli.commands.main", new_callable=AsyncMock)
    def test_start_command_custom_options(self, mock_main: AsyncMock, runner: CliRunner) -> None:
        """Test the `start` command with custom options."""
        result = runner.invoke(
            cli,
            [
                "start",
                "--username",
                "custom_user",
                "--token",
                "custom_token",
                "--timeout",
                "20",
                "--testbed",
                "--database",
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            username="custom_user",
            token="custom_token",  # noqa: S106
            api_timeout=20,
            testbed=True,
            use_database=True,
            verbose=True,
        )

    @patch("chaturbate_poller.cli.commands.main", new_callable=AsyncMock)
    def test_start_command_invalid_timeout(self, mock_main: AsyncMock, runner: CliRunner) -> None:
        """Test the `start` command with invalid timeout value."""
        result = runner.invoke(cli, ["start", "--timeout", "invalid"])
        assert result.exit_code == 2
        mock_main.assert_not_awaited()

    @patch("chaturbate_poller.cli.commands.main", new_callable=AsyncMock)
    def test_start_command_polling_error(self, mock_main: AsyncMock, runner: CliRunner) -> None:
        """Test the `start` command when PollingError is raised."""
        mock_main.side_effect = PollingError("Test polling error")

        result = runner.invoke(
            cli,
            ["start", "--username", "test_user", "--token", "test_token"],
        )

        assert result.exit_code == 1
        mock_main.assert_awaited_once()

    @patch("chaturbate_poller.cli.commands.main", new_callable=AsyncMock)
    def test_start_command_keyboard_interrupt(
        self, mock_main: AsyncMock, runner: CliRunner
    ) -> None:
        """Test the `start` command when KeyboardInterrupt is raised."""
        mock_main.side_effect = KeyboardInterrupt()

        result = runner.invoke(
            cli,
            ["start", "--username", "test_user", "--token", "test_token"],
        )

        assert result.exit_code == 0
        mock_main.assert_awaited_once()

    @patch("chaturbate_poller.cli.commands.main", new_callable=AsyncMock)
    def test_start_command_cancelled_error(self, mock_main: AsyncMock, runner: CliRunner) -> None:
        """Test the `start` command when asyncio.CancelledError is raised."""
        mock_main.side_effect = asyncio.CancelledError()

        result = runner.invoke(
            cli,
            ["start", "--username", "test_user", "--token", "test_token"],
        )

        assert result.exit_code == 0
        mock_main.assert_awaited_once()
