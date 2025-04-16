# Dockerfile.dev
FROM python:3.12.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && apt-get clean

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Disable Poetry creating its own venvs (we're in Docker, we use system Python)
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install only dependencies first for caching
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# Copy actual source code
COPY app/ ./app

# Default command
CMD ["poetry", "run", "start"]
