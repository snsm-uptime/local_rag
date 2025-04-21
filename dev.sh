#!/bin/bash
set -e

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

./scripts/check_base_rebuild.sh

echo "🛠️ Building all services..."
docker-compose -f docker-compose.dev.yml build

echo "🧪 Running tests..."
docker-compose -f docker-compose.dev.yml run --rm test

echo "✅ Tests passed! Launching backend and CLI..."
docker-compose -f docker-compose.dev.yml up -d cli backend
