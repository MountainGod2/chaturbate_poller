# Install uv
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

FROM python:3.12-slim

# Copy the virtual environment
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Create log directory
RUN mkdir -p /app/logs

# Change the working directory to the `app` directory
WORKDIR /app

# Ensure the docker-entrypoint.sh script is copied
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set the default entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
