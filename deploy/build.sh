#!/bin/sh
set -eux

docker build \
    --build-arg API_URL="${API_URL}" \
    --build-arg ARCHIVE_URL="${ARCHIVE_URL}" \
    --tag ark_ui \
    --file ui/deploy.Dockerfile ui

docker build \
    --tag ark_api \
    --file api/deploy.Dockerfile api
