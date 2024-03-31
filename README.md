
# Chaturbate Poller

Chaturbate Poller is a Python application designed to periodically fetch and process events from the Chaturbate API. It utilizes asynchronous HTTP requests and parses the received events for further processing or storage.

## Features

- Asynchronous event fetching from the Chaturbate API.
- Error handling and retry logic for network requests.
- Logging of fetched events and error conditions for audit and debugging.
- Environment variable-based configuration for API credentials.

## Requirements

- Python 3.8+
- httpx
- Pydantic
- asyncio
- dotenv

## Setup

To set up the Chaturbate Poller, follow these steps:

1. Ensure Python 3.8 or higher is installed on your system.
3. Install the Python package:

```bash
pip install chaturbate-poller
```

3. Set up your environment variables by creating a `.env` file in the root directory with the following content:

```
CB_USERNAME=your_chaturbate_username
CB_TOKEN=your_api_token
```

Replace `your_chaturbate_username` and `your_api_token` with your actual Chaturbate username and API token.

## Usage

To run the Chaturbate Poller, use the following command from the root directory of the project:

```bash
python -m chaturbate_poller
```

The application will start, log into the console, and begin fetching events from the Chaturbate API using the credentials provided in the `.env` file.

See `example.py` for more detailed usage instructions.

## Development

For development purposes, especially to run tests or develop additional features, consider setting up a virtual environment and installing the development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\Activate`
pip install -r requirements-dev.txt
```

To run tests:

```bash
pytest
```

## Contributing

Contributions to the Chaturbate Poller are welcome! Please follow the standard fork-and-pull request workflow on GitHub to submit your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Credits

`chaturbate_poller` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
