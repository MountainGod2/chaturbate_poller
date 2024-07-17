# Chaturbate Event Listener

## Description

Chaturbate Event Listener is a tool for polling and processing events from the Chaturbate API. It includes both a command-line interface (CLI) and a Python API for integration into other scripts or applications.

## Features

- Polls events from the Chaturbate API
- Handles various event types such as tips, user messages, and broadcast start/stop
- Retries on server errors with exponential backoff
- Configurable via environment variables
- Includes detailed logging with sanitized URLs

## Installation

To install this project, you can use [pip](https://pypi.org/project/pip/):

```bash
pip install chaturbate-event-listener
```

## Configuration

Create a `.env` file in the root directory of your project and add the following environment variables:

```text
CHATURBATE_USERNAME="YOUR_CHATURBATE_USERNAME"
CHATURBATE_TOKEN="YOUR_CHATURBATE_API_TOKEN"
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL (Optional, default is INFO)
```

## Usage

### Command-Line Interface (CLI)

To use the CLI, run the following command:

```bash
python -m chaturbate_event_listener --username YOUR_USERNAME --token YOUR_TOKEN
```

You can also pass additional options:

- `--timeout`: Set the API request timeout (default: 10 seconds)
- `--testbed`: Use the testbed URL for testing
- `--debug`: Enable debug logging

Example:

```bash
python -m chaturbate_event_listener --username testuser --token testtoken --timeout 20 --testbed --debug
```

### Python API

You can also integrate Chaturbate Event Listener into your own script:

```python
import asyncio

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.event_poller import EventPoller


async def main():
    config = Config(
        username="YOUR_CHATURBATE_USERNAME",
        token="YOUR_CHATURBATE_API_TOKEN",
        timeout=10
    )
    poller = EventPoller(config)

    await poller.poll()


if __name__ == "__main__":
    asyncio.run(main())

```

Or with an optional callback (see [example](examples/example.py) for more detail):

```python
import asyncio

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.event_poller import EventPoller


def handle_tip_event(event):
    username = event.object.user.username
    tokens = event.object.tip.tokens

    print("%s tipped: %s tokens", username, tokens)


async def main() -> None:
    config = Config(
        username="YOUR_CHATURBATE_USERNAME",
        token="YOUR_CHATURBATE_API_TOKEN",
        use_testbed=True,
    )
    poller = EventPoller(config)

    poller.register_callback("tip", handle_tip_event)

    await poller.poll()


if __name__ == "__main__":
    asyncio.run(main())

```

## Logging

The project uses the `rich` library for enhanced logging. Logs are sanitized to remove sensitive information such as usernames and tokens from URLs.

## Tests

To run the tests, use `pytest`. Make sure you have installed the development dependencies:

```bash
poetry install --with dev
pytest
```

## GitHub Actions

The project includes GitHub Actions workflows for continuous integration (CI) and CodeQL analysis.

- `.github/workflows/ci-cd.yml`: CI/CD pipeline for testing, linting, and deploying the project.
- `.github/workflows/codeql.yml`: CodeQL analysis for security scanning.
- `.github/workflows/dependabot.yml`: Dependabot configuration for automatic dependency updates.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Maintained by MountainGod2. For any inquiries, please contact `admin@reid.ca`.
