FROM ghcr.io/astral-sh/uv:0.7.13-python3.13-alpine AS builder

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN uv venv

COPY pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock && \
    uv sync --frozen --no-install-project --no-editable --compile-bytecode --no-dev

# Project installation stage
FROM builder AS project

COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --compile-bytecode --no-dev

# Final image stage
FROM ghcr.io/astral-sh/uv:0.7.13-python3.13-alpine AS final

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=project --chown=appuser:appgroup /app/.venv /app/.venv

COPY --chown=appuser:appgroup docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

VOLUME /app/logs

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python.*chaturbate_poller" > /dev/null || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
