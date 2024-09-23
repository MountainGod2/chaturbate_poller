# Chaturbate Poller

Chaturbate Poller is an asynchronous Python library designed to interface with the Chaturbate API.

[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/ci-cd.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fci-cd.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/ci-cd.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)

## Key Features

- **Error Management**: Implements error handling and retry logic to manage network inconsistencies.
- **Configurable Logging**: Detailed logging mechanisms for debugging and monitoring the poller's operations.
- **Data Persistence**: Integrates with InfluxDB for storing event data, enabling further analysis and monitoring.

## Installation

Ensure Python 3.11+ is installed, then run:

```bash
pip install chaturbate-poller
```

## Configuration

Create a `.env` file at the root with the necessary environment variables:

```text
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"
USE_DATABASE="true"
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller"
INFLUXDB_BUCKET="your_bucket"
INFLUXDB_INIT_MODE="setup"
INFLUXDB_INIT_USERNAME="admin"
INFLUXDB_INIT_PASSWORD="changeme"
INFLUXDB_INIT_ORG="chaturbate-poller"
INFLUXDB_INIT_BUCKET="my-bucket"
```

## Usage

The Chaturbate Poller can be used both as a library and a CLI tool. Below is an example of how to use it as a library to fetch events:

```python
import asyncio
from chaturbate_poller.chaturbate_client import ChaturbateClient

async def main():
    async with ChaturbateClient('your_username', 'your_token') as client:
        events = await client.fetch_events()
        for event in events:
            print(event)

if __name__ == "__main__":
    asyncio.run(main())
```

### CLI Usage

```bash
python -m chaturbate_poller --username <your_username> --token <your_token>
```

## Docker Usage

To run using Docker, pull the latest Docker image and run:

```bash
docker pull ghcr.io/mountaingod2/chaturbate_poller:latest
docker run \
  -e CB_USERNAME="your_chaturbate_username" \
  -e CB_TOKEN="your_chaturbate_api_token" \
  -e INFLUXDB_URL="http://influxdb:8086" \
  -e INFLUXDB_TOKEN="your_influxdb_token" \
  -e INFLUXDB_ORG="chaturbate-poller" \
  -e INFLUXDB_BUCKET="my-bucket" \
  -v /opt/chaturbate_poller:/app \ # Log storage only
  ghcr.io/mountaingod2/chaturbate_poller:latest --testbed
```

## Development

Set up a virtual environment and install dependencies for development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
```

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- Chaturbate API
- Python Asyncio Library
- HTTPX for HTTP client capabilities
- InfluxDB for data storage

`chaturbate_poller` was created with the help of [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
