# src/chaturbate_event_listener/__init__.py
r"""A Chaturbate event listener.

This package provides a client to listen to events from the Chaturbate Events API.

Example usage::

        async with ChaturbateEventClient(username, token) as client:
            await client.process_events()

"""

from importlib.metadata import version

__version__ = version("chaturbate_event_listener")
__author__ = "MountainGod2"
__author_email__ = "admin@reid.ca"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "admin@reid.ca"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_event_listener"
__description__ = "A Chaturbate event listener."

__all__: list[str] = []
