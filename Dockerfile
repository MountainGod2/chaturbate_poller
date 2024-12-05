# Stage 1: Build stage using the python:3.13-alpine image
FROM python:3.13-alpine AS builder

# Install necessary build dependencies for Python packages
RUN apk add --no-cache git gcc musl-dev libffi-dev openssl-dev && \
    pip install --no-cache-dir uv

# Define the working directory for the builder container
WORKDIR /app

# Copy the application source code and metadata into the builder image
COPY pyproject.toml README.md ./

# Set up a virtual environment and install the project dependencies into it
RUN uv venv -n /app/.venv && \
    uv pip compile -n pyproject.toml -o requirements.txt && \
    uv pip sync -n requirements.txt

# Stage 2: Final runtime image using the python:3.13-alpine image
FROM python:3.13-alpine AS runtime

LABEL org.opencontainers.image.title="Chaturbate Events API Python Library" \
      org.opencontainers.image.description="Python library for interacting with the Chaturbate Events API" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.license="MIT" \
      org.opencontainers.image.url="https://github.com/mountaingod2/chaturbate_poller" \
      org.opencontainers.image.source="https://github.com/mountaingod2/chaturbate_poller" \
      org.opencontainers.image.documentation="https://mountaingod2.github.io/chaturbate_poller/" \
      org.opencontainers.image.os="alpine" \
      org.opencontainers.image.arch="x86_64"

# Configure environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Define the working directory for the runtime container
WORKDIR /app

# Copy the virtual environment from the builder image to the runtime image
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code into the runtime image
COPY src/ /app/src/
COPY pyproject.toml README.md LICENSE ./

# Install the application into the virtual environment
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install -n .

# Copy the entrypoint script into the runtime image and make it executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Set the default entrypoint for the container
ENTRYPOINT ["/app/docker-entrypoint.sh"]
