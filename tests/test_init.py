"""Test the chaturbate event listener initialization."""

from chaturbate_event_listener import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __maintainer__,
    __maintainer_email__,
    __url__,
    __version__,
)


def test_metadata() -> None:
    """Test the package metadata."""
    assert __author__ == "MountainGod2"
    assert __author_email__ == "admin@reid.ca"
    assert __description__ == "A Chaturbate event listener."
    assert __license__ == "MIT"
    assert __maintainer__ == "MountainGod2"
    assert __maintainer_email__ == "admin@reid.ca"
    assert __url__ == "https://github.com/MountainGod2/chaturbate_event_listener"
    assert __version__ == "0.1.0"
