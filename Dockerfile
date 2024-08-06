FROM python:3.12-slim

# Set environment variables to prevent Poetry from creating a virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the entire project to the container
COPY . /app

# Install dependencies
RUN poetry install --no-root

# Ensure the current directory is in the PYTHONPATH
ENV PYTHONPATH=/app/src

# Set the entrypoint or default command
CMD ["python", "-m", chaturbate_poller]
