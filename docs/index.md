# Chaturbate Poller

Python library and CLI tool for interacting with the Chaturbate Events API. Monitor and analyze chat activity, tips, room status changes, and other events in real-time.

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv pip install chaturbate-poller

# Using pip
pip install chaturbate-poller
```

### Basic Usage

```bash
# CLI usage
chaturbate_poller start --username your_username --token your_token

# Docker
docker run -e CB_USERNAME="user" -e CB_TOKEN="token" ghcr.io/mountaingod2/chaturbate_poller:latest
```

### Python API

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
            url = response.next_url

asyncio.run(main())
```

## Features

**Real-time Event Tracking**
: Monitor chat messages, tips, room status changes, and other events with configurable polling intervals

**Robust Error Handling**
: Automatic retries with exponential backoff, detailed error classification, and connection recovery

**Comprehensive Logging**
: Structured JSON logs for machine parsing and console-friendly output with rich formatting

**Data Persistence**
: Optional InfluxDB integration for time-series storage with pre-configured analytics queries

## Configuration

Create a `.env` file with your credentials:

```ini
CB_USERNAME="your_chaturbate_username"
CB_TOKEN="your_chaturbate_token"

# Optional: InfluxDB integration
INFLUXDB_URL="http://influxdb:8086"
INFLUXDB_TOKEN="your_influxdb_token"
INFLUXDB_ORG="chaturbate-poller"
INFLUXDB_BUCKET="events"
USE_DATABASE="false"
```

Get your API token at [chaturbate.com/statsapi/authtoken/](https://chaturbate.com/statsapi/authtoken/) with "Events API" permission enabled.

## CLI Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--username TEXT` | Chaturbate username | From `.env` |
| `--token TEXT` | API token | From `.env` |
| `--timeout FLOAT` | Request timeout (seconds) | 10.0 |
| `--database / --no-database` | Enable InfluxDB | Disabled |
| `--testbed / --no-testbed` | Use testbed environment | Disabled |
| `--verbose / --no-verbose` | Enable detailed logging | Disabled |

```{toctree}
:maxdepth: 2
:hidden:

API Reference <api/index>
examples
deployment
development
```
