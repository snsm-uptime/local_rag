#!/bin/bash
set -eo pipefail

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Validate local-rag-base exists
if ! docker image inspect local-rag-base:latest >/dev/null 2>&1; then
  echo "📦 Base image [local-rag-base:latest] not found. Building from Dockerfile.base..."
  docker build -f Dockerfile.base -t local-rag-base:latest .
else
  echo "✅ Base image [local-rag-base:latest] found locally. Skipping base build."
fi

# Check if rebuild logic needs to run
./scripts/check_base_rebuild.sh

echo "🛠️ Building all services..."
docker-compose -f docker-compose.dev.yml build

echo "🧪 Running tests..."
docker-compose -f docker-compose.dev.yml run --rm --service-ports test

echo "✅ Tests passed! Launching backend and CLI..."
docker-compose -f docker-compose.dev.yml up -d cli backend