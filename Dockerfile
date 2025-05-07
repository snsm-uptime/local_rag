# ----------------------------
# 🚧 Stage 1: base (dependencies only)
# ----------------------------
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_CACHE_DIR=/root/.cache/pip \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/root/.cache/pypoetry

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl build-essential libgl1 libglib2.0-0 poppler-utils && \
    apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-root --with dev

RUN mkdir -p /opt/poetry_deps && \
    cp -r /usr/local/lib/python3.12/site-packages/* /opt/poetry_deps

# ----------------------------
# 🧪 Stage 2: dev (full source + debugger support)
# ----------------------------
FROM python:3.12-slim AS dev

WORKDIR /app
COPY --from=base /opt/poetry_deps /opt/poetry_deps
COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/opt/poetry_deps:/app:$PYTHONPATH"

EXPOSE 8000 5678
CMD ["python", "-m", "app.dev"]

# ----------------------------
# 🚀 Stage 3: prod (lean runtime)
# ----------------------------
FROM python:3.12-slim AS prod

WORKDIR /app
COPY --from=base /opt/poetry_deps /opt/poetry_deps
COPY app ./app
COPY entrypoints ./entrypoints

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/opt/poetry_deps:/app:$PYTHONPATH"

EXPOSE 8000
CMD ["python", "-m", "app.prod"]
