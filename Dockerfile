# syntax=docker/dockerfile:1.8@sha256:e87caa74dcb7d46cd820352bfea12591f3dba3ddc4285e19c7dcd13359f7cefd

# Base stage with Python 3.12 and necessary dependencies
FROM python:3.12-alpine@sha256:aeff64320ffb81056a2afae9d627875c5ba7d303fb40d6c0a43ee49d8f82641c AS base

# Install essential packages, including bash and gcc
RUN apk update && apk add --no-cache bash gcc

# Copy the 'uv' binary from the latest UV image to the /bin directory
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:60b38e00ed04730baa97f6348074351ef3ed654778c9a63022c3c7075844fc0e /uv /bin/uv

# Create a Python virtual environment using UV
RUN uv venv --python=python3.12 /app/.venv


# Dependencies stage: compile and sync Python dependencies
FROM base AS dependencies

WORKDIR /app

# Copy the project configuration file (pyproject.toml)
COPY pyproject.toml README.md ./

# Compile requirements and sync using UV, ensuring no cache is used
RUN uv pip compile pyproject.toml -o requirements.txt --no-cache \
    && uv pip sync requirements.txt --no-cache


# Final production stage
FROM python:3.12-alpine@sha256:aeff64320ffb81056a2afae9d627875c5ba7d303fb40d6c0a43ee49d8f82641c AS production

# Set environment variables for optimal Python performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VENV_PATH="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the virtual environment from the dependencies stage
COPY --from=dependencies /app/.venv .venv

# Copy necessary project files
COPY README.md pyproject.toml docker-entrypoint.sh ./
COPY src/ src/

# Install project dependencies and ensure entrypoint script is executable
RUN --mount=from=ghcr.io/astral-sh/uv:latest@sha256:60b38e00ed04730baa97f6348074351ef3ed654778c9a63022c3c7075844fc0e,source=/uv,target=/bin/uv \
    uv pip install . --no-cache \
    && chmod +x ./docker-entrypoint.sh

# Set the default entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
