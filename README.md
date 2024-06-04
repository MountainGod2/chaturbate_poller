[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/ci-cd.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fci-cd.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/ci-cd.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)

# Chaturbate Event Listener

Chaturbate Event Listener is a Python package that allows you to poll the Chaturbate Events API for real-time events such as broadcasts, user interactions, tips, and more. This package provides standalone CLI option, as well as functions for integrating Chaturbate event data into your applications or scripts.

## Features

- Polls the Chaturbate Events API for real-time events.
- Handles various types of events, including broadcast start/stop, user interactions, tips, and more.
- Customizable event handling with support for user-defined event handlers.
- Supports both production and testbed environments for Chaturbate API.

## Installation

You can install Chaturbate Event Listener via [pip](https://pip.pypa.io/):

```bash
pip install chaturbate-event-listener
```

## Usage

### CLI Interface

Chaturbate Event Listener provides a CLI interface for easy execution.

```bash

chaturbate-event-listener <username> <token> [--timeout TIMEOUT] [--use-testbed] [--verbose]

    <username>: Your Chaturbate username.
    <token>: Your Chaturbate API token.
    --timeout TIMEOUT: (Optional) Timeout for the event feed (default is 10 seconds).
    --use-testbed: (Optional) Use the Chaturbate testbed API.
    --verbose: (Optional) Enable verbose logging output.
```
You can run the CLI with the following command:
```bash
python -m chaturbate_event_listener example_user example_token
```
Or with the optional values:
```bash
python -m chaturbate_event_listener example_user example_token --timeout=30 --use-testbed --verbose
```
## Example

Here's an example of how to use the Chaturbate Event Listener in a script:

```python

import asyncio
import os

from chaturbate_event_listener.client import ChaturbateEventClient

async def handle_event(message: dict) -> None:
    """Custom event handler."""
    print(f"Received event: {message}")

async def main() -> None:
    """Run the Chaturbate Events API client."""
    user = os.getenv("CHATURBATE_USERNAME", "")
    token = os.getenv("CHATURBATE_TOKEN", "")

    client = ChaturbateEventClient(
        username=user,
        token=token,
        event_handler=handle_event,
        is_testbed=True,  # Use testbed environment
    )

    async with client:
        await client.process_events()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

Chaturbate Event Listener supports configuration via environment variables:

```
    CHATURBATE_USERNAME: Your Chaturbate username.
    CHATURBATE_TOKEN: Your Chaturbate API token.
```

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, feel free to open an issue or submit a pull request.

Before contributing, please make sure to read the Contribution Guidelines.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Credits

Chaturbate Event Listener is developed and maintained by MountainGod2.
