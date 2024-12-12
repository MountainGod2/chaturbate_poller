"""chaturbate_poller package."""

from importlib.metadata import version

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.format_messages import format_message

__version__ = version("chaturbate_poller")
__author__ = "MountainGod2"
__author_email__ = "admin@reid.ca"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "admin@reid.ca"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_poller"
__description__ = "Python library for interacting with the Chaturbate Events API."


__all__: list[str] = ["ChaturbateClient", "ConfigManager", "format_message"]
