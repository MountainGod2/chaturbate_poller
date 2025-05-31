# Deployment Guide

## Docker Deployment

### Single Container

```bash
docker run -d \
  --name chaturbate-poller \
  -e CB_USERNAME="your_username" \
  -e CB_TOKEN="your_token" \
  -v /host/logs:/app/logs \
  ghcr.io/mountaingod2/chaturbate_poller:latest --verbose
```

### Docker Compose with InfluxDB

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  chaturbate-poller:
    image: ghcr.io/mountaingod2/chaturbate_poller:latest
    environment:
      - CB_USERNAME=your_username
      - CB_TOKEN=your_token
      - INFLUXDB_URL=http://influxdb:8086
      - INFLUXDB_TOKEN=your_influxdb_token
      - INFLUXDB_ORG=chaturbate-poller
      - INFLUXDB_BUCKET=events
      - USE_DATABASE=true
    command: ["--database", "--verbose"]
    depends_on:
      - influxdb
    volumes:
      - ./logs:/app/logs

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=password
      - DOCKER_INFLUXDB_INIT_ORG=chaturbate-poller
      - DOCKER_INFLUXDB_INIT_BUCKET=events
    volumes:
      - influxdb_data:/var/lib/influxdb2

volumes:
  influxdb_data:
```

Launch with:

```bash
docker-compose up -d
```

## InfluxDB Analytics

### Sample Queries

**Event count by type (last 24 hours)**:
```javascript
from(bucket: "events")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r._field == "method")
  |> group(columns: ["_value"])
  |> count()
  |> sort(columns: ["_value"], desc: true)
```

**Total tips received (last 7 days)**:
```javascript
from(bucket: "events")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "chaturbate_events")
  |> filter(fn: (r) => r.method == "tip")
  |> filter(fn: (r) => r._field == "object.tip.tokens")
  |> sum()
```

**Top chatters by message count**:
```javascript
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

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CB_USERNAME` | Chaturbate username | Yes |
| `CB_TOKEN` | API token from Chaturbate | Yes |
| `INFLUXDB_URL` | InfluxDB server URL | No |
| `INFLUXDB_TOKEN` | InfluxDB authentication token | No |
| `INFLUXDB_ORG` | InfluxDB organization | No |
| `INFLUXDB_BUCKET` | InfluxDB bucket name | No |
| `USE_DATABASE` | Enable InfluxDB integration | No |

## Production Considerations

- Use persistent volumes for logs and InfluxDB data
- Configure proper network security for InfluxDB access
- Monitor container health and resource usage
- Set up log rotation for persistent storage
- Consider using secrets management for sensitive credentials
