# Use the official Python image from the Docker Hub
FROM python:3.11-slim-buster

# Install the program and its dependencies using pip
RUN pip install chaturbate-poller

# Set working directory
WORKDIR /app

# Create a non-root user and switch to it
RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser

# Run the program
ENTRYPOINT ["python", "-m", "chaturbate_poller"]
