# Chaturbate Poller

Chaturbate Poller is an asynchronous Python library designed to interface with the Chaturbate API. It allows you to efficiently poll events, handle event data, and optionally store the results in InfluxDB for analysis or monitoring purposes.

[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/ci-cd.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fci-cd.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/ci-cd.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)

## Key Features

- **Resilient Error Handling**: Includes retry logic and robust error management to handle intermittent network issues.
- **Customizable Logging**: Built-in, configurable logging to help track and debug the poller's operations.
- **Data Persistence**: Supports integration with InfluxDB to store event data for further analysis and monitoring.

## Installation

Ensure that Python 3.11 or later is installed, then install the package using `pip`:

```bash
pip install chaturbate-poller
```

## Configuration

Before running the poller, configure the environment by creating a `.env` file at the root of your project. This file should contain your Chaturbate API credentials and optional InfluxDB settings:

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

Chaturbate Poller can be used both as a Python library and a command-line tool.

### As a Library

Below is a simple example of how to use Chaturbate Poller to fetch events asynchronously:

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

### As a Command-Line Tool

You can also run the poller directly from the command line:

```bash
python -m chaturbate_poller --username <your_username> --token <your_token>
```

For a complete list of CLI options, use the `--help` flag.

```bash
python -m chaturbate_poller --help
```

## Docker Usage

Chaturbate Poller is also available as a Docker image. To run it, use the following commands:

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

For development, it's recommended to create a virtual environment and install dependencies with [uv](https://docs.astral.sh/uv/):

```bash
pip install uv
git clone https://github.com/MountainGod2/chaturbate_poller.git .
cd chaturbate_poller
uv venv .venv
uv pip install .
```

## Contributing

Contributions are always welcome! To contribute:

1. Fork the repository.
2. Create a new feature branch.
3. Submit a pull request.

Please ensure your changes pass all tests and follow the repository's coding standards.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

Chaturbate Poller is built using the following technologies:

- [Chaturbate API](https://chaturbate.com)
- [Python's Asyncio Library](https://docs.python.org/3/library/asyncio.html)
- [HTTPX](https://www.python-httpx.org/) for handling HTTP requests
- [InfluxDB](https://www.influxdata.com/) for data storage
