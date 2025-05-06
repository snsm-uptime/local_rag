#!/bin/bash

# This script compares the current hash of pyproject.toml and poetry.lock
# to a stored hash value. If they differ, it triggers a rebuild of the base image.

BASE_HASH_FILE=".base_image.hash"
CURRENT_HASH=$(cat pyproject.toml poetry.lock | sha256sum | awk '{print $1}')

if [ ! -f "$BASE_HASH_FILE" ]; then
  echo "📦 No base hash found. Building base image..."
  docker build -t local-rag-base -f Dockerfile.base .
  echo "$CURRENT_HASH" > "$BASE_HASH_FILE"
else
  STORED_HASH=$(cat "$BASE_HASH_FILE")

  if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
    echo "🔁 Lock files changed. Rebuilding base image..."
    docker build -t local-rag-base -f Dockerfile.base .
    echo "$CURRENT_HASH" > "$BASE_HASH_FILE"
  else
    echo "✅ No changes in dependencies. Skipping base rebuild."
  fi
fi
