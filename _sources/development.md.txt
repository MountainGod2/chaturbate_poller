# Development Guide

## Setup Development Environment

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/MountainGod2/chaturbate_poller.git
cd chaturbate_poller

# Install dependencies with uv
uv sync --all-extras

# Or with pip
pip install -e ".[dev,docs]"

# Set up pre-commit hooks
pre-commit install
```

### Environment Configuration

Create a `.env` file for development:

```ini
CB_USERNAME="your_test_username"
CB_TOKEN="your_test_token"
USE_DATABASE="false"
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=chaturbate_poller

# Run specific test file
uv run pytest tests/test_client.py

# Run tests in parallel
uv run pytest -n auto
```

## Code Quality

### Linting and Formatting

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Individual tools
uv run ruff check src/
uv run ruff format src/
uv run mypy src/
uv run pylint src/
```

### Type Checking

The project uses type hints throughout. Run type checking with:

```bash
uv run mypy src/
```

## Building Documentation

```bash
# Install docs dependencies
uv sync --group=docs

# Build HTML documentation
uv run sphinx-build -b html docs docs/_build/html

# Serve locally
python -m http.server 8000 -d docs/_build/html
```

## Project Structure

```
src/chaturbate_poller/
├── __init__.py          # Package exports
├── cli/                 # Command-line interface
├── client/              # API client implementation
├── logging_config/      # Logging configuration
├── database_handler/    # InfluxDB integration
└── models.py            # Pydantic data models
```

## Contributing

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Create Branch**: Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make Changes**: Implement your changes with appropriate tests
4. **Run Tests**: Ensure all tests pass and code quality checks succeed
5. **Commit**: Use conventional commit messages
6. **Push**: Push to your fork and create a pull request

### Commit Message Convention

```
type(scope): description

feat(client): add support for new event types
fix(database): resolve connection timeout issues
docs(readme): update installation instructions
test(client): add tests for error handling
```

### Pull Request Guidelines

- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass
- Keep changes focused and atomic
- Write clear commit messages

## Release Process

Releases are automated using semantic-release:

1. Commits following conventional format trigger version bumps
2. GitHub Actions runs tests and builds packages
3. Successful builds are automatically published to PyPI
4. Docker images are built and pushed to GitHub Container Registry

## Debugging

### Enabling Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Using Testbed Environment

```bash
# Use Chaturbate's testbed for development
chaturbate_poller start --testbed --verbose
```

### Common Issues

**Import Errors**: Ensure you've installed the package in development mode with `pip install -e .`

**API Token Issues**: Verify your token has "Events API" permission at [chaturbate.com/statsapi/authtoken/](https://chaturbate.com/statsapi/authtoken/)

**Connection Timeouts**: Check network connectivity and consider increasing the `--timeout` value
