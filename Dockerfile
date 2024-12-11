# Stage 1: Build stage using the python:3.13-alpine image
FROM python:3.13-alpine AS builder

# Install necessary build dependencies for Python packages
RUN apk add --no-cache git gcc musl-dev libffi-dev openssl-dev && \
    pip install --no-cache-dir uv

# Define the working directory for the builder container
WORKDIR /app

# Copy the application metadata files into the builder image
COPY pyproject.toml README.md ./

# Set up a virtual environment and install the project dependencies into it
RUN uv venv -n /app/.venv && \
    uv pip compile -n pyproject.toml -o requirements.txt && \
    uv pip sync -n requirements.txt

# Stage 2: Final runtime image using the python:3.13-alpine image
FROM python:3.13-alpine AS runtime

# Configure environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Define the working directory for the runtime container
WORKDIR /app

# Copy the virtual environment and application code from the builder image
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/
COPY pyproject.toml README.md LICENSE ./

# Declare a volume for logs
VOLUME /app/logs

# Copy the entrypoint script into the runtime image and make it executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Install the application into the virtual environment
RUN --mount=from=ghcr.io/astral-sh/uv:0.5.8,source=/uv,target=/bin/uv \
    uv pip install -n .

# Set the default entrypoint for the container
ENTRYPOINT ["/app/docker-entrypoint.sh"]
