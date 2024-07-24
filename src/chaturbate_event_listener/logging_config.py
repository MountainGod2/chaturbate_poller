"""Logging configuration for the Chaturbate event listener."""

import logging
import re

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_traceback

install_traceback(show_locals=True)

URL_REGEX = re.compile(r"events/([^/]+)/([^/]+)")


def sanitize_url(url: str) -> str:
    """Sanitize the URL by replacing username and token with placeholders."""
    return URL_REGEX.sub(r"events/USERNAME/TOKEN", url)


class SanitizeURLFilter(logging.Filter):
    """Logging filter to sanitize sensitive information from URLs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to sanitize URLs."""
        if isinstance(record.msg, str):
            record.msg = sanitize_url(record.msg)
        if record.args:
            record.args = tuple(sanitize_url(str(arg)) for arg in record.args)
        return True


def setup_logging(*, debug: bool = False) -> None:
    """Setup logging configuration.

    Args:
        debug (bool): Whether to enable debug logging.
    """
    console = Console()
    console.rule("[bold red]Chaturbate Event Listener")

    log_format = "%(name)s - %(message)s"
    log_level = logging.DEBUG if debug else logging.INFO

    handler = RichHandler(console=console, show_time=True, show_path=False)
    handler.addFilter(SanitizeURLFilter())

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[handler],
    )

    logging.getLogger("asyncio").setLevel(logging.WARNING)
