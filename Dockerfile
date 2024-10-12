# Stage 1: Build stage using uv
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY pyproject.toml README.md ./
COPY src/ ./src

# Install the project dependencies using uv
RUN uv lock --no-cache && uv sync --frozen --no-editable --no-dev --no-cache --no-install-project

# Stage 2: Prepare the final runtime image (Alpine, minimal)
FROM python:3.12-alpine AS runtime

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the necessary project files and virtual enviroment from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/README.md /app/

# Install the project using temporary uv installation
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv pip install . --no-cache-dir

# Ensure the docker-entrypoint.sh script is copied and executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set the default entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
