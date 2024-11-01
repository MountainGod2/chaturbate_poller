# Chaturbate Poller

**Chaturbate Poller** is a Python library for interacting with the Chaturbate API. It allows you to poll events asynchronously, handle various event types, and optionally store event data in InfluxDB for further analysis or monitoring.

[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/ci-cd-build.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fci-cd-build.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/ci-cd-build.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)

## Features

- **Event Polling**: Fetch events from the Chaturbate API using Python's asyncio.
- **Error Handling**: Includes retry logic for basic error handling during polling.
- **Optional Logging**: Configurable logging to keep track of polling activity.
- **InfluxDB Support**: Optionally store events in InfluxDB if data storage is required.

## Installation

Make sure you have Python 3.11 or later installed, then install the package:

```bash
pip install chaturbate-poller
```

## Configuration

To get started, create a `.env` file in the root of your project directory. This file will store your API credentials and (if applicable) InfluxDB connection details:

```text
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller"
INFLUXDB_BUCKET="your_bucket"
USE_DATABASE="true"  # Enable if you plan to use InfluxDB
```

> [!NOTE]
> To create an API token, click here: [https://chaturbate.com/statsapi/authtoken/](https://chaturbate.com/statsapi/authtoken/)

> [!IMPORTANT]
> Ensure you have the "**Events API**" permission selected before generating

## Usage

### Command-Line Tool

You run Chaturbate Poller directly from the command line:

```bash
python -m chaturbate_poller --username <your_username> --token <your_token>
```

For more options:

```bash
python -m chaturbate_poller --help
```

### Docker Usage

To run Chaturbate Poller in a Docker container:

```bash
docker pull ghcr.io/mountaingod2/chaturbate_poller:latest
```

```bash
docker run \
  -e CB_USERNAME="your_chaturbate_username" \
  -e CB_TOKEN="your_chaturbate_token" \
  ghcr.io/mountaingod2/chaturbate_poller:latest --verbose --testbed
```

### Library Example

You can also import it into your programs. Here’s a simple example of how to fetch events in a loop using the library asynchronously:

```python
import asyncio

from chaturbate_poller import ChaturbateClient

async def main():
    async with ChaturbateClient("your_username", "your_token") as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:

                # Do something with the received events
                print(event.dict())

            url = response.next_url

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/MountainGod2/chaturbate_poller.git
   cd chaturbate_poller
   ```

2. Install dependencies using [uv](https://docs.astral.sh/uv/):
   ```bash
   uv venv .venv
   uv pip install -e .
   ```

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a new feature branch.
3. Submit a pull request.

Please ensure that any changes pass tests and follow coding guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
