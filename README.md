# Chaturbate Poller

Chaturbate Poller is a Python application designed to periodically fetch and process events from the Chaturbate API. It utilizes asynchronous HTTP requests and parses the received events for further processing or storage.

[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/ci-cd.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fci-cd.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/ci-cd.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)

## Features

- **Asynchronous event fetching** from the Chaturbate API.
- **Error handling and retry logic** for network requests.
- **Logging** of fetched events and error conditions for audit and debugging.
- **Environment variable-based configuration** for API credentials.

## Requirements

- Python 3.8+
- httpx
- pydantic
- asyncio
- python-dotenv

## Setup

To set up the Chaturbate Poller, follow these steps:

1. Ensure Python 3.8 or higher is installed on your system.
2. Install the Python package:

    ```bash
    pip install chaturbate-poller
    ```

3. Set up your environment variables by creating a `.env` file in the root directory with the following content:

    ```bash
    CB_USERNAME="your_chaturbate_username"
    CB_TOKEN="your_api_token"
    ```

    Replace `your_chaturbate_username` and `your_api_token` with your actual Chaturbate username and API token.

## Usage Examples

Here's a basic example to get you started with fetching events from the Chaturbate API:

```python
import asyncio
import logging
import os

from chaturbate_poller import ChaturbateClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")

async def main() -> None:
    async with ChaturbateClient(username, token, 20) as client:
        response = await client.fetch_events()
        for event in response.events:
            logging.info(event.dict())  # Log the event as a dictionary

if __name__ == "__main__":
    asyncio.run(main())
```

The application will start and begin fetching and printing events from the Chaturbate API using the credentials provided in the `.env` file.

For more detailed usage examples, including handling specific event types and using the included Pydantic models, see the `examples/` directory.

## Development

To set up a development environment, especially to run tests or develop additional features, consider setting up a virtual environment and installing the development dependencies:

1. Create a virtual environment and activate it:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\Activate`
    ```

2. Install the development dependencies:

    ```bash
    pip install -r requirements-dev.txt
    ```

3. To run tests:

    ```bash
    pytest
    ```

## Contributing

Contributions to the Chaturbate Poller are welcome! Please follow the standard fork-and-pull request workflow on GitHub to submit your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

`chaturbate_poller` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
