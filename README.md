# Chaturbate Poller

[![Documentation](https://img.shields.io/readthedocs/chaturbate-poller)](https://chaturbate-poller.readthedocs.io/en/stable/)
[![PyPI Version](https://img.shields.io/pypi/v/chaturbate-poller)](https://pypi.org/project/chaturbate-poller/)
[![Python Version](https://img.shields.io/pypi/pyversions/chaturbate-poller)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/github/actions/workflow/status/MountainGod2/chaturbate_poller/cd.yml?branch=main&label=tests)](https://github.com/MountainGod2/chaturbate_poller/actions/workflows/cd.yml/)
[![Coverage](https://img.shields.io/codecov/c/github/MountainGod2/chaturbate_poller/main)](https://app.codecov.io/gh/MountainGod2/chaturbate_poller/)
[![License](https://img.shields.io/pypi/l/chaturbate-poller)](https://github.com/MountainGod2/chaturbate_poller)

Python library and CLI for monitoring Chaturbate Events API. Real-time event tracking with automatic error handling and optional InfluxDB integration.

## Features

- **Real-time event monitoring** - Chat messages, tips, room status changes, and user interactions
- **Robust error handling** - Automatic retries with exponential backoff and connection recovery
- **Structured data output** - Clean event formatting with type-safe models
- **Database integration** - Optional InfluxDB support for analytics and time-series data
- **Flexible configuration** - Environment variables, CLI options, or programmatic setup

## Installation

### Using uv (recommended)

```bash
uv pip install chaturbate-poller
```

### Using pip

```bash
pip install chaturbate-poller
```

### CLI without installation

```bash
uvx chaturbate_poller start
```

### API Token

Generate your API token at [https://chaturbate.com/statsapi/authtoken/](https://chaturbate.com/statsapi/authtoken/) with "Events API" permission.

## Quick Start

### CLI Usage

```bash
# Direct credentials
chaturbate_poller start --username your_username --token your_token

# Testbed environment
chaturbate_poller start --testbed --verbose

# Environment configuration
chaturbate_poller start
```

### Environment Configuration

Create a `.env` file in your project root:

```ini
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"

# Optional InfluxDB configuration
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller" 
INFLUXDB_BUCKET="events"
```

## Usage

### CLI Options

```bash
chaturbate_poller start [OPTIONS]
```

Key options:
- `--username TEXT` - Chaturbate username
- `--token TEXT` - API token  
- `--timeout FLOAT` - Request timeout in seconds (default: 10.0)
- `--database` - Enable InfluxDB integration
- `--testbed` - Use testbed environment
- `--verbose` - Enable detailed logging

### Docker

```bash
docker run -e CB_USERNAME="username" -e CB_TOKEN="token" \
  ghcr.io/mountaingod2/chaturbate_poller:latest --verbose
```

### Docker Compose

```bash
cp .env.example .env
# Configure credentials in .env
docker-compose up -d
```

## Programmatic Usage

### Basic Client

```python
import asyncio
from chaturbate_poller import ChaturbateClient

async def main():
    async with ChaturbateClient("username", "token") as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                print(f"Event: {event.method}")
                print(event.model_dump_json(indent=2))
            url = response.next_url

asyncio.run(main())
```

### Event Handling

```python
from chaturbate_poller import ChaturbateClient, format_message

async def process_events():
    async with ChaturbateClient("username", "token") as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                if event.method == "tip":
                    amount = event.object.tip.tokens
                    user = event.object.user.username
                    print(f"Tip: {user} -> {amount} tokens")
                elif event.method == "chatMessage":
                    message = format_message(event)
                    print(f"Chat: {message}")
            url = response.next_url
```

## InfluxDB Integration

Enable with `--database` flag to store events for analytics. See [sample queries](/influxdb_queries.flux) for data analysis examples.

## Development

```bash
git clone https://github.com/MountainGod2/chaturbate_poller.git
cd chaturbate_poller
uv sync --all-extras
uv run pytest
```

## Documentation

- [API Reference](https://chaturbate-poller.readthedocs.io/)
- [Examples and Tutorials](https://chaturbate-poller.readthedocs.io/)

## Contributing

Pull requests welcome. Fork the repository, create a feature branch, add tests, and submit a PR.

## License

[MIT License](/LICENSE)
