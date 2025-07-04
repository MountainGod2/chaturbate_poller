# =============================================================================
# BUILD STAGE
# =============================================================================
FROM ghcr.io/astral-sh/uv:0.7.19-python3.13-alpine AS builder

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/app/.venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN uv venv

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --no-editable --compile-bytecode --no-dev

# =============================================================================
# RUNTIME STAGE
# =============================================================================
FROM python:3.13-alpine AS final

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/app/.venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

COPY --chown=appuser:appgroup docker-entrypoint.sh ./
RUN chmod +x /app/docker-entrypoint.sh

RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

VOLUME /app/logs

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python.*chaturbate_poller" > /dev/null || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
