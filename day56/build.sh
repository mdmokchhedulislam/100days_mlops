#!/bin/bash
# Shell-based CI pipeline for the ml-ci-app image.
#
# Stages: test -> build -> tag (git SHA) -> push to local registry.
# Run from /root/code/ci/.
set -euo pipefail

cd "$(dirname "$0")"

IMAGE="ml-ci-app"
REGISTRY="localhost:5555"

# --- Stage 1: test
echo "[ci] stage 1/4 — running tests"
python3 -m pytest app/test_app.py

# --- Stage 2: build
echo "[ci] stage 2/4 — building image"
docker build -t "$IMAGE:latest" app/

# --- Stage 3: tag with short git SHA
echo "[ci] stage 3/4 — tagging"
SHA=$(git -C app rev-parse --short HEAD)
TAGGED="$REGISTRY/$IMAGE:$SHA"
docker tag "$IMAGE:latest" "$TAGGED"

# --- Stage 4: push
echo "[ci] stage 4/4 — pushing"
docker push "$TAGGED"

echo "[ci] complete: $TAGGED"