FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir chaturbate-poller

# Set the entrypoint or default command
CMD ["python", "-m", "chaturbate_poller"]
