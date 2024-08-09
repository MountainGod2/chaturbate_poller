# Use an official Python runtime as a parent image
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment in /venv
RUN python -m venv /venv

# Activate virtual environment and upgrade pip
ENV PATH="/venv/bin:$PATH"
RUN pip install --upgrade pip

# Install the latest version of the chaturbate-poller package
RUN pip install --no-cache-dir chaturbate-poller

# Create a new stage for the final image
FROM python:3.11-slim

# Copy the virtual environment from the builder stage
COPY --from=builder /venv /venv

# Set the path to use the virtual environment
ENV PATH="/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Command to run the application
ENTRYPOINT ["python", "-m", "chaturbate_poller"]
