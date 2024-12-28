from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from chaturbate_poller.cli import cli


class TestCLI:
    """Tests for the CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for Click CLI runner."""
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

    @patch("chaturbate_poller.cli.ConfigManager")
    @patch("chaturbate_poller.cli.main", new_callable=AsyncMock)
    def test_start_command_defaults(
        self, mock_main: AsyncMock, mock_config_manager: AsyncMock, runner: CliRunner
    ) -> None:
        """Test the `start` command with default options."""
        mock_config_manager.return_value.get.side_effect = lambda key, default: {
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

    @patch("chaturbate_poller.cli.main", new_callable=AsyncMock)
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

    @patch("chaturbate_poller.cli.main", new_callable=AsyncMock)
    def test_start_command_missing_required_args(
        self, mock_main: AsyncMock, runner: CliRunner
    ) -> None:
        """Test the `start` command when required arguments are missing."""
        result = runner.invoke(cli, ["start", "--username", "", "--token", ""])
        assert result.exit_code != 0
        assert "Chaturbate username and token are required." in result.output
        mock_main.assert_not_awaited()
