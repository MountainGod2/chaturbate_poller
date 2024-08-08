# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install the program and its dependencies using pip
RUN pip install --no-cache-dir chaturbate-poller

# Set working directory
WORKDIR /app

# Run the program
ENTRYPOINT ["python", "-m", "chaturbate_poller"]
