"""Tests for chaturbate_event_listener CLI."""

from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from chaturbate_event_listener.__main__ import main
from chaturbate_event_listener.cli import run


@pytest.fixture()
def runner() -> CliRunner:
    """Return a CliRunner instance."""
    return CliRunner()


def test_main(runner: CliRunner, caplog: pytest.LogCaptureFixture) -> None:
    """Test the main function."""
    with patch("chaturbate_event_listener.cli.run", new_callable=AsyncMock) as mock_run:
        result = runner.invoke(
            main,
            ["test_user", "test_token", "--timeout", "5", "--use-testbed", "--verbose"],
        )
        assert result.exit_code == 0
        mock_run.assert_called_once()
        assert "Starting asyncio.run" in caplog.text
        assert "Exiting main" in caplog.text


@pytest.mark.asyncio()
async def test_run() -> None:
    """Test the run function."""
    with patch(
        "chaturbate_event_listener.client.ChaturbateEventClient.__aenter__", AsyncMock()
    ) as mock_enter:
        mock_enter.return_value = mock_enter
        with patch(
            "chaturbate_event_listener.client.ChaturbateEventClient.__aexit__",
            AsyncMock(),
        ):
            await run("test_user", "test_token", timeout=5, use_testbed=True)
            mock_enter.process_events.assert_called_once()
