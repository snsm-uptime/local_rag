#!/bin/bash
set -euo pipefail

BASE_IMAGE_NAME="rag-dev-base"
HASH_FILE=".base_image.dev.hash"
HASH_INPUT="pyproject.toml poetry.lock"

CURRENT_HASH=$(cat $HASH_INPUT | sha256sum | awk '{print $1}')
IMAGE_EXISTS=$(docker image inspect "$BASE_IMAGE_NAME:latest" >/dev/null 2>&1 && echo true || echo false)

if [[ "$IMAGE_EXISTS" == "false" ]]; then
  echo "📦 Base image [$BASE_IMAGE_NAME:latest] not found. Building..."
  docker build --target base -t "$BASE_IMAGE_NAME" -f Dockerfile .
  echo "$CURRENT_HASH" > "$HASH_FILE"
  exit 0
fi

if [[ ! -f "$HASH_FILE" ]]; then
  echo "📦 Hash file missing. Rebuilding base image..."
  docker build --target base -t "$BASE_IMAGE_NAME" -f Dockerfile .
  echo "$CURRENT_HASH" > "$HASH_FILE"
  exit 0
fi

STORED_HASH=$(cat "$HASH_FILE")

if [[ "$CURRENT_HASH" != "$STORED_HASH" ]]; then
  echo "🔁 Dependencies changed. Rebuilding base image..."
  docker build --target base -t "$BASE_IMAGE_NAME" -f Dockerfile .
  echo "$CURRENT_HASH" > "$HASH_FILE"
else
  echo "✅ Base image [$BASE_IMAGE_NAME] is up to date. Skipping rebuild."
fi
