"""chaturbate_poller package."""

import logging.config

# Read version from installed package
from importlib.metadata import version

from .chaturbate_poller import ChaturbateClient
from .logging_config import LOGGING_CONFIG

__version__ = version("chaturbate_poller")
__author__ = "MountainGod2"
__author_email__ = "admin@reid.ca"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "admin@reid.ca"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_poller"
__description__ = "A Chaturbate event poller."


# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
"""logging.Logger: The logger for the package."""

__all__ = ["ChaturbateClient", "logger"]
"""List[str]: The package exports."""
