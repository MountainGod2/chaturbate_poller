# Stage 1: Build stage using the lightweight python:3.12-alpine image
FROM python:3.12-alpine AS builder

# Install necessary build dependencies for Python packages that require compilation
RUN apk add --no-cache git gcc musl-dev libffi-dev openssl-dev && \
    pip install uv

# Define the working directory for the build process
WORKDIR /app

# Copy essential project files to optimize the build cache and avoid unnecessary rebuilds
COPY pyproject.toml README.md ./

# Set up a virtual environment and install dependencies, ensuring no cache is used to reduce image size
RUN uv venv /app/.venv --no-cache && \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip sync requirements.txt

# Stage 2: Final runtime image using alpine to minimize the overall size
FROM python:3.12-alpine AS runtime

# Configure environment variables to use the virtual environment in the final image
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Define the working directory for the runtime container
WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code and metadata into the runtime image
COPY src/ /app/src/
COPY pyproject.toml README.md LICENSE ./

# Install the project package in the virtual environment without using the cache, reducing image size
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install . --no-cache-dir

# Copy the entrypoint script to the appropriate location and make it executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Set the default entrypoint for the container, ensuring the correct startup script is executed
ENTRYPOINT ["/app/docker-entrypoint.sh"]
