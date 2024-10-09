FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy the project files into the image
COPY src/ pyproject.toml ./

# Install the project dependencies using uv
RUN uv lock --no-cache && uv sync --frozen --no-editable --no-dev --no-cache

# Stage 2: Prepare the final runtime image
FROM python:3.12-alpine AS runtime

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
