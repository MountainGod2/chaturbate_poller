# Use an official Python runtime as a parent image
FROM python:3.11-buster AS builder

# Set environment variables
ENV POETRY_VERSION=1.4.2

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set working directory
WORKDIR /app

# Copy only the dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies without dev dependencies
RUN poetry install --without dev --no-root

# Copy the remaining files
COPY . .

# Install the package
RUN poetry install --without dev

# Create the final image
FROM python:3.11-slim-buster AS runtime

# Set environment variables
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the virtual environment from the builder image
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /app /app

# Set the working directory
WORKDIR /app

# Set the command to run the application
CMD ["poetry", "run", "chaturbate_poller"]
