FROM python:3.13-alpine3.21

# Configure virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy metadata and documentation
COPY pyproject.toml uv.lock LICENSE README.md ./

# Copy application source code
COPY src/ /app/src/

# Install dependencies and application
RUN --mount=from=ghcr.io/astral-sh/uv:0.7.6,source=/uv,target=/usr/local/bin/uv \
    uv venv -n /app/.venv && \
    uv pip sync -n pyproject.toml && \
    uv pip install -n .

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

# Define log volume
VOLUME /app/logs

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
