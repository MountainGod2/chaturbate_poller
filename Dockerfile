# Use the official Python image from the Docker Hub
FROM python:3.11-slim-buster

# Install Poetry
RUN pip install poetry==1.4.2

# Set working directory
WORKDIR /app

# Copy only the dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Install dependencies without dev dependencies
RUN poetry install --only main

# Create a non-root user and switch to it
RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"

# Command to run the CLI program
ENTRYPOINT ["poetry", "run", "chaturbate_poller"]
