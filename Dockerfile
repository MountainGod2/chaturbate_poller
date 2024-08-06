FROM python:3.12-slim

# Set environment variables to prevent Poetry from creating a virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy pyproject.toml and poetry.lock to the container
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-dev

# Copy the rest of the application code to the container
COPY . /app

# Ensure the current directory is in the PYTHONPATH
ENV PYTHONPATH=/app/src

# Set the entrypoint or default command
CMD ["poetry", "run", "python", "-m", "chaturbate_poller"]
