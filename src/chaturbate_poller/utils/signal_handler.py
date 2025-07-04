"""Signal handler utilities for the Chaturbate Poller."""

from __future__ import annotations

import logging
import signal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio

logger: logging.Logger = logging.getLogger(name=__name__)


class SignalHandler:
    """Handles system signals for graceful shutdown."""

    def __init__(self, loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]) -> None:
        """Initialize the signal handler.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.
            stop_future (asyncio.Future[None]): Future to signal when stopping.
        """
        self.loop: asyncio.AbstractEventLoop = loop
        self.stop_future: asyncio.Future[None] = stop_future
        self._registered_signals: list[signal.Signals] = []

    def setup(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        signals_to_handle = [signal.SIGINT, signal.SIGTERM]

        for sig in signals_to_handle:
            try:
                self.loop.add_signal_handler(sig, self._signal_handler, sig)
                self._registered_signals.append(sig)
                logger.debug("Registered signal handler for %s", sig.name)
            except NotImplementedError:
                # Signal handling not available on this platform
                logger.warning("Signal handling not available for %s", sig.name)

    def _signal_handler(self, sig: signal.Signals) -> None:
        """Handle received signals.

        Args:
            sig (signal.Signals): The received signal.
        """
        logger.info("Received signal %s, shutting down gracefully...", sig.name)
        if not self.stop_future.done():
            self.stop_future.set_result(None)

    def cleanup(self) -> None:
        """Clean up registered signal handlers."""
        for sig in self._registered_signals:
            try:
                self.loop.remove_signal_handler(sig)
                logger.debug("Removed signal handler for %s", sig.name)
            except ValueError:
                # Handler was already removed
                pass
        self._registered_signals.clear()
