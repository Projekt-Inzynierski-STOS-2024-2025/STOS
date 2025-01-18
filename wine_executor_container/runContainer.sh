#!/bin/bash

if [ -z "$1" ]; then
    echo "Required argument - shared volume path"
    exit 1
fi

SHARED_VOLUME_PATH=$1

docker run --rm -v "$SHARED_VOLUME_PATH":/app/project executor