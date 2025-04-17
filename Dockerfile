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

# Poetry and Python settings
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1
ENV POETRY_CACHE_DIR=/root/.cache/pypoetry
ENV PYTHONPATH="/opt/poetry_deps:$PYTHONPATH"

# Set working directory
WORKDIR /app

# Copy only dependency files
COPY pyproject.toml poetry.lock ./

# Install main deps with poetry (to system)
RUN poetry install --no-root --only main

# Install dev-only tools directly into shared volume
RUN pip install --target /opt/poetry_deps debugpy watchdog

# Copy app code
COPY app/ ./app

# Expose app + debug ports
EXPOSE 80 5678

# Copy and set entrypoint
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
