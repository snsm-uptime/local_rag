#!/bin/bash
set -euo pipefail

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Compose file references
COMPOSE_FILES="-f docker-compose.dev.yml -f docker-compose.dev.override.yml"

# Parse optional flag
DEBUG_TESTS=false
if [[ "${1:-}" == "--debug-tests" ]]; then
  DEBUG_TESTS=true
fi

echo "🔍 Checking base image and dependency cache..."
bash ./scripts/rebuild_base_if_needed.dev.sh

if [[ "$DEBUG_TESTS" == true ]]; then
  echo "🐞 Starting debug-test service..."
  docker-compose $COMPOSE_FILES run --rm --service-ports debug-test
else
  echo "🧪 Running fast tests (no debug)..."
  docker-compose $COMPOSE_FILES run --rm test

  echo "🚀 Starting backend and CLI containers..."
  docker-compose $COMPOSE_FILES up -d backend cli
fi
