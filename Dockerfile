FROM python:3.13-alpine3.22 AS base

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app

ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_SYSTEM_PYTHON=1

LABEL org.opencontainers.image.title="chaturbate-poller"
LABEL org.opencontainers.image.description="Python library for interacting with the Chaturbate Events API"
LABEL org.opencontainers.image.source="https://github.com/MountainGod2/chaturbate_poller"

COPY pyproject.toml uv.lock README.md ./

FROM base AS release

WORKDIR /app

COPY src/ /app/src/

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    uv pip install .

FROM release AS service

WORKDIR /app

COPY --chown=appuser:appgroup docker-entrypoint.sh ./

RUN chmod +x docker-entrypoint.sh

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python.*chaturbate_poller" > /dev/null || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
