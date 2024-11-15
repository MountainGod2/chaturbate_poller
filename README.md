<div align="center">

# Chaturbate Poller

[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/docker-build.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fdocker-build.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/docker-build.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)

</div>

**Chaturbate Poller** is a Python library and CLI for polling events from the Chaturbate API. It provides asynchronous event handling, logging, and optional integration with InfluxDB to store event data for analysis.

## Features

- **Event Polling**: Efficiently poll events from Chaturbate’s API.
- **Error Handling**: Includes backoff and retry mechanisms.
- **Logging**: Console and JSON file logging for structured insights.
- **Optional InfluxDB Storage**: Store events in InfluxDB for analysis or monitoring.

## Installation

Ensure Python 3.11 or later is installed, then install via pip:

```bash
pip install chaturbate-poller
```

## Configuration

Create a `.env` file in your project’s root directory for API and InfluxDB credentials:

```text
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller"
INFLUXDB_BUCKET="your_bucket"
USE_DATABASE="false"  # Set to `true` if InfluxDB is used
```

> [!NOTE]
> [Generate an API token here](https://chaturbate.com/statsapi/authtoken/) with the "Events API" permission enabled.

## Usage

### CLI

Start the poller from the command line:

```bash
python -m chaturbate_poller start --username <your_username> --token <your_token>
```

For additional options:

```bash
python -m chaturbate_poller --help
```

### Docker

Run Chaturbate Poller in Docker:

```bash
docker pull ghcr.io/mountaingod2/chaturbate_poller:latest
```

```bash
docker run \
  -e CB_USERNAME="your_chaturbate_username" \
  -e CB_TOKEN="your_chaturbate_token" \
  ghcr.io/mountaingod2/chaturbate_poller:latest --verbose --testbed
```

### Library Usage

To use Chaturbate Poller as a library, here's a sample script to fetch events in a loop:

```python
import asyncio
from chaturbate_poller import ChaturbateClient

async def main():
    async with ChaturbateClient("your_username", "your_token") as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                print(event.dict())  # Process each event

            url = response.next_url

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

1. Clone the repository:

   ```bash
   git clone https://github.com/MountainGod2/chaturbate_poller.git
   cd chaturbate_poller
   ```

2. Set up the environment and dependencies using [uv](https://docs.astral.sh/uv/):

   ```bash
   uv venv .venv
   uv pip install -e .
   ```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request, ensuring tests and coding standards are met.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
