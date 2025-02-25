#!/bin/bash

if [ -z "$1" ]; then
    echo "Required executable path"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Required input files"
    exit 1
fi

if [ -z "$3" ]; then
    echo "Required output directory"
    exit 1
fi

EXECUTABLE=$1
INPUT_FILES=$2
OUTPUT_DIR=$3

docker run --rm -v "$EXECUTABLE":/app/project/source -v "$INPUT_FILES":/app/project/input -v "$OUTPUT_DIR":/app/project/output executor