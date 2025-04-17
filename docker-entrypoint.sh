#!/bin/bash
set -e

echo "🔁 Starting in watch mode with debugpy on port 5678..."

exec poetry run python -m debugpy \
  --listen 0.0.0.0:5678 \
  --wait-for-client \
  -m watchdog.watchmedo auto-restart \
    --directory=./app \
    --pattern="*.py" \
    --recursive \
    -- \
    python -m start
