ENV PYTHONDONTWRITEBYTECODE=1

FROM python:3.11-slim

RUN pip install --no-cache-dir --no-compile chaturbate-poller

WORKDIR /app

ENTRYPOINT ["python", "-m", "chaturbate_poller"]
