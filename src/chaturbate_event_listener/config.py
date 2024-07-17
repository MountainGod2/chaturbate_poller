"""Chaturbate Event Poller configuration.

This module provides a CLI tool to poll events from the Chaturbate API.

Example:
    To start the event poller, run the following command:

        $ python -m chaturbate_event_listener \
          --username <username> \
          --token <token>

    Replace `<username>` and `<token>` with your Chaturbate username and token.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Constants
UNAUTHORIZED_ERROR = 401
SERVER_ERROR_STATUS_CODE_THRESHOLD = 500
MAXIMUM_TIMEOUT = 90


# Configuration Class
class Config(BaseSettings):
    """A configuration class."""

    username: str
    token: str
    timeout: int = Field(default=10, le=MAXIMUM_TIMEOUT)
    use_testbed: bool = False

    @property
    def base_url(self) -> str:
        """Get the base URL.

        Returns:
            str: The base URL based on whether testbed is used.
        """
        return (
            "https://events.testbed.cb.dev/events"
            if self.use_testbed
            else "https://eventsapi.chaturbate.com/events"
        )

    @property
    def url(self) -> str:
        """Get the API URL.

        Returns:
            str: The full API URL including username, token, and timeout.
        """
        url = f"{self.base_url}/{self.username}/{self.token}?timeout={self.timeout}"
        return str(url)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        arbitrary_types_allowed=True,
    )
