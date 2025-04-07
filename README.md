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

A robust Python library and CLI tool for interacting with the Chaturbate Events API. Monitor and analyze chat activity, tips, room status changes, and other events in real-time with support for structured logging, automated error handling, and optional InfluxDB integration.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [CLI Usage](#cli-usage)
  - [Docker](#docker)
  - [Docker Compose](#docker-compose)
- [InfluxDB Integration](#influxdb-integration)
- [Programmatic Usage](#programmatic-usage)
- [Development](#development)
- [Documentation](#documentation)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Real-time Event Tracking**
  - Monitor chat messages, tips, room status changes, and other events
  - Configurable polling intervals with automatic rate limiting
  - Support for both production and testbed environments

- **Robust Error Handling**
  - Automatic retries with exponential backoff for transient errors
  - Detailed error classification and reporting
  - Connection recovery after network interruptions

- **Comprehensive Logging**
  - Structured JSON logs for machine parsing
  - Console-friendly output with rich formatting
  - Configurable verbosity levels for debugging

- **Data Persistence & Analytics**
  - Optional InfluxDB integration for time-series storage
  - Pre-configured sample queries for common analytics use cases
  - Efficient data retention policies for long-term storage

## Installation

Here are a few ways to install the package:

### Using uv (Recommended)

Install with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install chaturbate-poller
```

### Using pip

Make sure you have Python 3.12+ installed:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install chaturbate-poller
```

### Using uvx (for CLI tool isolation)

Run the CLI without installing it in your Python environment:

```bash
uvx chaturbate_poller start
```

### Environment Configuration

Create a `.env` file with your credentials:

```ini
# Required for API access
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"

# Optional: InfluxDB settings (if using --database flag)
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller"
INFLUXDB_BUCKET="my-bucket"
USE_DATABASE="false"  # Set to "true" to enable InfluxDB integration
```

**API Token:** You'll need to generate your token at [chaturbate.com/statsapi/authtoken/](https://chaturbate.com/statsapi/authtoken/) with "Events API" permission enabled.

## Quick Start

```bash
# With uv
uv run chaturbate_poller start --username your_username --token your_token

# Using testbed mode (for development/testing)
uv run chaturbate_poller start --testbed --verbose

# With pip installation
python -m chaturbate_poller start --username your_username --token your_token
```

## Usage

### CLI Usage

The command-line interface makes it easy to interact with the Chaturbate Events API:

```bash
chaturbate_poller start [OPTIONS]
```

#### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--username TEXT` | Your Chaturbate username | From `.env` file |
| `--token TEXT` | Your API token | From `.env` file |
| `--timeout FLOAT` | API request timeout in seconds | 10.0 |
| `--database / --no-database` | Enable InfluxDB integration | Disabled |
| `--testbed / --no-testbed` | Use testbed environment | Disabled |
| `--verbose / --no-verbose` | Enable detailed logging | Disabled |
| `--help` | Show help message and exit | |

For complete CLI documentation:

```bash
chaturbate_poller --help
```

### Docker

Run the poller in a container with all dependencies included:

```bash
# Pull the latest image
docker pull ghcr.io/mountaingod2/chaturbate_poller:latest

# Run with environment variables
docker run -d \
  --name chaturbate-poller \
  -e CB_USERNAME="your_chaturbate_username" \
  -e CB_TOKEN="your_chaturbate_token" \
  ghcr.io/mountaingod2/chaturbate_poller:latest --verbose
```

### Docker Compose

For a complete setup including InfluxDB for data persistence:

1. **Clone the configuration:**

   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit with your credentials
   nano .env
   ```

2. **Launch the services:**

   ```bash
   docker-compose up -d
   ```

3. **Pass additional arguments**:

   ```bash
   # Via environment variable
   POLLER_ARGS="--verbose --testbed" docker-compose up -d
   ```

4. **Access InfluxDB** at [http://localhost:8086](http://localhost:8086)

## InfluxDB Integration

When enabled with the `--database` flag, events are stored in InfluxDB for analytics and visualization.

### Sample Queries

Here are some useful InfluxDB Flux queries to analyze your Chaturbate data:

```flux
// Event count by type (last 24 hours)
from(bucket: "events")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r._field == "method")
  |> group(columns: ["_value"])
  |> count()
  |> sort(columns: ["_value"], desc: true)

// Total tips received (last 7 days)
from(bucket: "events")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r.method == "tip")
  |> filter(fn: (r) => r._field == "object.tip.tokens")
  |> sum()

// Top chatters by message count (last 24 hours)
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

For more examples, check out the `/config/chaturbate_poller/influxdb_queries.flux` file.

## Programmatic Usage

You can integrate the library into your own Python applications:

### Basic Example

```python
import asyncio
from chaturbate_poller import ChaturbateClient

async def main():
    async with ChaturbateClient("your_username", "your_token") as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                # Process each event
                print(f"Event type: {event.method}")
                print(event.model_dump_json(indent=2))

            # Use the next URL for pagination
            url = response.next_url

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Event Handlers

```python
import asyncio
from chaturbate_poller import ChaturbateClient
from chaturbate_poller.models import TipEvent, ChatMessageEvent

async def handle_tip(event: TipEvent) -> None:
    """Process tip events with custom logic."""
    username = event.object.user.username
    amount = event.object.tip.tokens
    print(f"Received {amount} tokens from {username}!")

    # Trigger special actions based on tip amount
    if amount >= 100:
        await send_special_thanks(username)

async def handle_chat(event: ChatMessageEvent) -> None:
    """Process chat message events."""
    username = event.object.user.username
    message = event.object.message
    print(f"{username}: {message}")

async def main():
    # Register handlers for specific event types
    handlers = {
        "tip": handle_tip,
        "chatMessage": handle_chat,
    }

    # Create client with custom handlers
    async with ChaturbateClient(
        "your_username",
        "your_token",
        event_handlers=handlers
    ) as client:
        # Start polling with automatic handler dispatch
        await client.poll_events()

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

    # Create client with database integration
    async with ChaturbateClient(
        "your_username",
        "your_token",
        database_writer=influx
    ) as client:
        await client.poll_events()

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

### Setup Development Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/MountainGod2/chaturbate_poller.git
   cd chaturbate_poller
   ```

2. **Install dependencies:**

   ```bash
   # Using uv (recommended)
   uv sync --all-extras

   # Or using pip
   pip install -e ".[dev,docs]"
   ```

3. **Set up pre-commit hooks:**

   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
uv run pytest

# With coverage report
uv run pytest --cov=chaturbate_poller --cov-report=html
```

## Documentation

### Building Docs Locally

```bash
# Install documentation dependencies
uv sync --extra=docs

# Build HTML documentation
uv run sphinx-build -b html docs docs/_build/html
```

Then open `docs/_build/html/index.html` in your browser.

### Online Documentation

Visit the [documentation](https://chaturbate-poller.readthedocs.io/) for comprehensive guides and API reference.

## Changelog

View the complete [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Run linting and tests (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

For more details, please read the [Contributing Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
