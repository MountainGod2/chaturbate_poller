FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy your application code to the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Set the entrypoint or default command
CMD ["python", "-m", "chaturbate_poller"]
