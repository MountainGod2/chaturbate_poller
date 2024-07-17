"""Logging configuration for the Chaturbate event listener."""

import logging
import re

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_traceback

install_traceback(show_locals=True)


def sanitize_url(url: str) -> str:
    """Sanitize the username and token in the URL."""
    return re.sub(r"events/([^/]+)/([^/]+)/", r"events/USERNAME/TOKEN/", url)


class SanitizeURLFilter(logging.Filter):
    """A logging filter that sanitizes the URL in the log message."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the log record.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            bool: Whether to include the log record.
        """
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Format the message before sanitization
            if record.args:
                record.msg = record.msg % record.args
                record.args = ()
            record.msg = sanitize_url(record.msg)
        return True


def setup_logging(*, debug: bool) -> None:
    """Setup logging.

    Args:
        debug (bool): Whether to enable debug logging.
    """
    console = Console()
    console.rule("[bold red]Chaturbate Event Listener")

    log_level = logging.DEBUG if debug else logging.INFO
    handler = RichHandler(console=console)
    handler.addFilter(SanitizeURLFilter())
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )
    logging.getLogger("asyncio").setLevel(logging.WARNING)
