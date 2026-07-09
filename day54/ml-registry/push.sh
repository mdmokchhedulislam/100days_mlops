#!/bin/bash
# Build the fraud-detector image and publish it to the local
# private registry so downstream clusters can pull by tag.
#
# Run from /root/code/ml-registry/.
set -euo pipefail

cd "$(dirname "$0")"

IMAGE="fraud-detector:v1"
REGISTRY="localhost:5555"

docker build -t "$IMAGE" .
docker tag "$IMAGE" "$REGISTRY/$IMAGE"

echo "Tagged $IMAGE as $REGISTRY/$IMAGE"

docker push $REGISTRY/$IMAGE
echo " $IMAGE pushed in $REGISTRY/$IMAGE"
