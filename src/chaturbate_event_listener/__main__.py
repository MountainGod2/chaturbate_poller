r"""Chaturbate event listener module.

This module provides a client to listen to events from the Chaturbate Events API.

Example usage::

        $ python -m chaturbate_event_listener <username> <token>

"""

from chaturbate_event_listener.cli import cli_main as main

if __name__ == "__main__":  # pragma: no cover
    main()
