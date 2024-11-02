"""chaturbate_poller package."""

# Read version from installed package
from importlib.metadata import version

from chaturbate_poller.chaturbate_client import ChaturbateClient

__version__ = version("chaturbate_poller")
__author__ = "MountainGod2"
__author_email__ = "admin@reid.ca"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "admin@reid.ca"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_poller"
__description__ = "Python library for interacting with the Chaturbate Events API."


__all__ = ["ChaturbateClient"]
"""List[str]: The package exports."""
