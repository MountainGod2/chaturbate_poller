# Use the official Python image as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry
RUN poetry install --no-dev

# Copy the application code
COPY src/ /app/src/
COPY examples/ /app/examples/
COPY .env.example /app/.env

# Run the application
CMD ["poetry", "run", "python", "-m", "chaturbate_poller"]
