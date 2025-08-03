"""chaturbate_poller package."""

import importlib.metadata

from chaturbate_poller.config.manager import ConfigManager
from chaturbate_poller.core.client import ChaturbateClient
from chaturbate_poller.utils.format_messages import format_message

__version__ = importlib.metadata.version(distribution_name="chaturbate_poller")
__author__ = "MountainGod2"
__author_email__ = "88257202+MountainGod2@users.noreply.github.com"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "88257202+MountainGod2@users.noreply.github.com"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_poller"
__description__ = "Python library for interacting with the Chaturbate Events API."


__all__: list[str] = ["ChaturbateClient", "ConfigManager", "format_message"]
