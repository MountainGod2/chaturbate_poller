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

# Install runtime dependencies (if needed)
RUN apk add --no-cache libffi openssl

# Set environment variables for UID and GID
ENV UID=99
ENV GID=100

# Create a group and user based on the environment variables
RUN if ! getent group "$GID"; then \
        addgroup -g "$GID" appgroup; \
    else \
        echo "Group with GID $GID already exists, skipping addgroup."; \
    fi && \
    adduser -u "$UID" -G appgroup -D appuser

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

# Create logs directory for the application
RUN mkdir -p /app/logs && \
    chown -R "$UID:$GID" /app/logs && \
    chmod -R 750 /app/logs

# Change ownership of the app directory to the non-root user
RUN chown -R "$UID:$GID" /app

# Install the application into the virtual environment
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install -n .

# Copy the entrypoint script into the runtime image and make it executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh && \
    chown "$UID:$GID" /app/docker-entrypoint.sh

# Switch to the non-root user
USER appuser

# Set the default entrypoint for the container
ENTRYPOINT ["/app/docker-entrypoint.sh"]
