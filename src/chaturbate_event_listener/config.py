"""Chaturbate Event Poller configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings

UNAUTHORIZED_ERROR = 401
SERVER_ERROR_STATUS_CODE_THRESHOLD = 500
MAXIMUM_TIMEOUT = 90


class Config(BaseSettings):
    """A configuration class."""

    username: str
    token: str
    timeout: int = Field(default=10, le=MAXIMUM_TIMEOUT)
    use_testbed: bool = False
    influxdb_url: str | None = None
    influxdb_token: str | None = None
    influxdb_org: str | None = None
    influxdb_bucket: str | None = None
    event_store_type: str = "console"

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
        return f"{self.base_url}/{self.username}/{self.token}?timeout={self.timeout}"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        extra = "ignore"
        arbitrary_types_allowed = True
