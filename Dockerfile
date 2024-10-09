# Stage 1: Install uv and dependencies
FROM python:3.12-slim AS builder

# Install uv from the uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory
WORKDIR /app

# Copy the project files into the image
COPY src/ pyproject.toml uv.lock ./

# Install the project dependencies using uv with caching enabled
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --no-dev

# Stage 2: Prepare the final runtime image
FROM python:3.12-slim AS runtime

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Set the working directory
WORKDIR /app

# Ensure the docker-entrypoint.sh script is copied and executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Set the default entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
