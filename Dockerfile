FROM python:3.12-slim

# Set environment variables to prevent Poetry from creating a virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy your application code and configuration files to the container
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-dev

# Copy the rest of your application code to the container
COPY . /app

# Set the entrypoint or default command
CMD ["poetry", "run", "python", "-m", "chaturbate_poller"]
