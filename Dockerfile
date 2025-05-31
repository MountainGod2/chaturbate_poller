FROM python:3.13-alpine3.21 AS base

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Configure virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY --chown=appuser:appgroup pyproject.toml uv.lock LICENSE README.md ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=ghcr.io/astral-sh/uv:0.7.9,source=/uv,target=/usr/local/bin/uv \
    uv venv && \
    uv sync --no-dev --no-cache

# Create a new stage for the final image
FROM base AS final

# Copy application files
COPY --chown=appuser:appgroup src/ ./src/

# Install application
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=ghcr.io/astral-sh/uv:0.7.9,source=/uv,target=/usr/local/bin/uv \
    uv pip install --no-deps .

# Copy and prepare entrypoint script
COPY --chown=appuser:appgroup docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

# Create logs directory
RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

# Define log volume
VOLUME /app/logs

# Switch to non-root user
USER appuser

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python.*chaturbate_poller" > /dev/null || exit 1

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
