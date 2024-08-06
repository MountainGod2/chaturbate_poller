FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && poetry install --no-dev

COPY . .

CMD ["poetry", "run", "python", "-m", "chaturbate_poller"]
