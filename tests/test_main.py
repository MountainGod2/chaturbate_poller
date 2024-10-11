import asyncio
import logging
from contextlib import suppress
from typing import Any

import pytest

from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.main import start_polling


class TestMain:
    """Tests for the main method."""

    @pytest.mark.asyncio
    async def test_start_polling_verbose(self, mocker: Any) -> None:
        """Test the start_polling function with verbose output."""
        with (
            suppress(KeyboardInterrupt),
        ):
            mocker.patch(
                "os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d
            )
            mocker.patch("sys.argv", ["test.py", "--verbose"])
            mocker.patch("asyncio.run", side_effect=lambda x: x)
            mocker.patch("chaturbate_poller.main.start_polling", return_value=None)
            # Mock coroutine _shutdown method and return a future
            mocker.patch(
                "chaturbate_poller.signal_handler.SignalHandler._shutdown",
                return_value=asyncio.Future(),
            )
            with pytest.raises(PollingError):
                await start_polling(
                    username="test_user",
                    token="test_token",  # noqa: S106
                    api_timeout=10,
                    testbed=False,
                    verbose=True,
                    event_handler=mocker.Mock(),
                )

    @pytest.mark.asyncio
    async def test_missing_username_or_token(self, mocker: Any, caplog: Any) -> None:
        """Test start_polling when username or token is missing."""
        mocker.patch.dict("os.environ", {"CB_USERNAME": "", "CB_TOKEN": ""})

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError, match="Chaturbate username and token are required."):
                await start_polling(
                    username="",
                    token="",
                    api_timeout=10,
                    testbed=False,
                    verbose=False,
                    event_handler=mocker.Mock(),
                )
