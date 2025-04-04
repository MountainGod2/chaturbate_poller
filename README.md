<div align="center">

# Chaturbate Poller

[![Read the Docs](https://img.shields.io/readthedocs/chaturbate-poller?link=https%3A%2F%2Fchaturbate-poller.readthedocs.io%2Fen%2Fstable%2F)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![Codecov Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main?link=https%3A%2F%2Fapp.codecov.io%2Fgh%2FMountainGod2%2Fchaturbate_poller)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/MountainGod2/chaturbate_poller?link=https%3A%2F%2Fwww.codefactor.io%2Frepository%2Fgithub%2Fmountaingod2%2Fchaturbate_poller)](https://www.codefactor.io/repository/github/mountaingod2/chaturbate_poller)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/cd.yml?branch=main&link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller%2Factions%2Fworkflows%2Fcd.yml)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/cd.yml/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller?link=https%3A%2F%2Fgithub.com%2FMountainGod2%2Fchaturbate_poller)](https://github.com/MountainGod2/chaturbate_poller?tab=MIT-1-ov-file)

[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller?link=https%3A%2F%2Fwww.python.org%2Fdownloads%2F)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/chaturbate-poller?link=https%3A%2F%2Fpypi.org%2Fproject%2Fchaturbate-poller%2F)](https://pypi.org/project/chaturbate-poller/)
[![Docker Image Version](https://img.shields.io/docker/v/mountaingod2/chaturbate_poller?sort=semver&label=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fmountaingod2%2Fchaturbate_poller)](https://hub.docker.com/r/mountaingod2/chaturbate_poller)
[![Docker Image Size](https://img.shields.io/docker/image-size/mountaingod2/chaturbate_poller?sort=semver&arch=amd64&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fmountaingod2%2Fchaturbate_poller%2Ftags)](https://hub.docker.com/r/mountaingod2/chaturbate_poller)

</div>

Python library and CLI tool for polling events from the Chaturbate API featuring asynchronous event handling, structured logging, and optional InfluxDB integration for analytics and monitoring.

---

## Features

- **Event Polling**:
  - Real-time tracking of chat messages, tips, room status changes, and more
  - Configurable polling intervals with automatic rate limiting
  - Support for both production and testbed environments

- **Error Handling**:
  - Automatic retries with exponential backoff for transient errors
  - Detailed error classification and reporting
  - Connection recovery after network interruptions

- **Logging**:
  - Structured JSON logs for machine parsing
  - Console-friendly output for human readability
  - Configurable verbosity levels

- **InfluxDB Integration**:
  - Store events in time-series format for analytics
  - Pre-configured dashboards for visualizing engagement metrics
  - Retention policies for efficient data management

---

## Installation

Choose one of the following installation methods:

### Using pip (Recommended)

Ensure Python 3.12 or later is installed, then install the package via pip:

```bash
pip install chaturbate-poller
```

### Using pipx (for CLI tool isolation)

For using only the CLI without affecting your Python environment:

```bash
pipx install chaturbate-poller
```

### Environment Configuration (Optional)

Create a `.env` file in your project's root directory with the following:

```text
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller"
INFLUXDB_BUCKET="my-bucket"
USE_DATABASE="false"  # Set to `true` if InfluxDB is used
```

> 💡 **Tip**: [Generate an API token here](https://chaturbate.com/statsapi/authtoken/) with "Events API" permission enabled.

---

## Quick Start

```bash
# Install the package
pip install chaturbate-poller

# Start polling with your credentials
python -m chaturbate_poller start --username your_username --token your_token

# To use the Chaturbate testbed API endpoint
python -m chaturbate_poller start --testbed --verbose
```

---

## Usage

### CLI Usage

Start the poller with the following command:

```bash
python -m chaturbate_poller start --username <your_username> --token <your_token>
```

#### Common CLI Options

- `--username`: Your Chaturbate username. Defaults to `.env` file value.
- `--token`: Your API token. Defaults to `.env` file value.
- `--timeout`: Timeout for API requests (default: 10 seconds).
- `--database`: Enable InfluxDB integration. Defaults to disabled.
- `--testbed`: Enable the testbed environment.
- `--verbose`: Enable detailed logging for debugging.

Run `python -m chaturbate_poller --help` for a complete list of options.

### Docker

To run the poller in Docker, pull the image and start the container:

```bash
docker pull ghcr.io/mountaingod2/chaturbate_poller:latest
docker run \
  -e CB_USERNAME="your_chaturbate_username" \
  -e CB_TOKEN="your_chaturbate_token" \
  ghcr.io/mountaingod2/chaturbate_poller:latest --verbose --database
```

### Docker Compose

This project includes a Docker Compose configuration for running the Chaturbate Poller with InfluxDB.

#### Setup

1. Create a `.env` file based on the `.env.example` template:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your credentials and settings.

3. Start the services:

   ```bash
   docker-compose up -d
   ```

#### Configuration Options

You can pass additional arguments to the poller service in two ways:

##### Using environment variables:

```bash
POLLER_ARGS="--verbose --testbed --database" docker-compose up -d
```

##### Using docker-compose run:

```bash
docker-compose run --rm chaturbate_poller --verbose --testbed
```

#### Accessing InfluxDB

The InfluxDB interface is available at http://localhost:8086 after startup by default.

---

## InfluxDB Integration

When the `--database` flag is enabled, events are stored in InfluxDB using the line protocol format. This enables analytics and visualization capabilities.

### Sample Queries

The following are examples of useful InfluxDB Flux queries for analyzing your Chaturbate data:

```text
// Count events by method in the last 24 hours
from(bucket: "events")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r._field == "method")
  |> group(columns: ["_value"])
  |> count()

// Calculate total tips received in the last 7 days
from(bucket: "events")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r.method == "tip")
  |> filter(fn: (r) => r._field == "object.tip.tokens")
  |> sum()

// Find most active users in the last 24 hours
from(bucket: "events")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r.method == "chatMessage")
  |> filter(fn: (r) => r._field == "object.user.username")
  |> group(columns: ["_value"])
  |> count()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 10)
```

A complete set of example queries can be found in the `/config/chaturbate_poller/influxdb_queries.flux` file. These queries can be used directly in the InfluxDB UI or imported into Grafana dashboards.

---

## Programmatic Usage

The library can be used directly in your Python code:

### Basic Usage

```python
import asyncio
from chaturbate_poller import ChaturbateClient

async def main():
    async with ChaturbateClient("your_username", "your_token", testbed=False) as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:

                # Do something with the event
                print(event.model_dump())

            url = response.next_url

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage: Custom Event Handlers

```python
import asyncio
from chaturbate_poller import ChaturbateClient
from chaturbate_poller.models import TipEvent

async def handle_tip(event: TipEvent):
    username = event.object.user.username
    amount = event.object.tip.tokens
    print(f"Received tip of {amount} tokens from {username}!")

    # You could trigger actions based on tip amount
    if amount >= 100:
        await send_special_thanks(username)

async def main():
    handlers = {
        "tip": handle_tip,
        # Add more handlers for different event types
    }

    async with ChaturbateClient(
        "your_username",
        "your_token",
        event_handlers=handlers
    ) as client:
        await client.poll_events()  # Built-in polling with handlers

if __name__ == "__main__":
    asyncio.run(main())
```

### With InfluxDB Integration

```python
import asyncio
from chaturbate_poller import ChaturbateClient, InfluxDBWriter

async def main():
    # Configure InfluxDB writer
    influx = InfluxDBWriter(
        url="http://localhost:8086",
        token="your_influxdb_token",
        org="your_org",
        bucket="events"
    )

    # Use with client
    async with ChaturbateClient(
        "your_username",
        "your_token",
        database_writer=influx
    ) as client:
        await client.poll_events()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Development

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/MountainGod2/chaturbate_poller.git
   cd chaturbate_poller
   ```

2. Install dependencies using [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync --all-extras
   ```

3. Set up pre-commit hooks (recommended):

   ```bash
   pre-commit install
   ```

### Running Tests

Run tests with `pytest`:

```bash
uv run pytest
```

For coverage report:

```bash
uv run pytest --cov=chaturbate_poller --cov-report=html
```

### Documentation

Build and preview the documentation locally:

```bash
uv sync --extra=docs
uv run sphinx-build -b html docs docs/_build/html
```

---

## Changelog

See the [CHANGELOG.md](CHANGELOG.md) file for a detailed history of changes.

---

## Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request, ensuring it includes tests and adheres to the coding standards.

Please review the [Contributing Guidelines](CONTRIBUTING.md) for more details.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
