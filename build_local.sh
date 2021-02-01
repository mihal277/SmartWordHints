#!/bin/bash

DEFAULTPORT=8081
PORT="${1:-$DEFAULTPORT}"

(docker stop smart-word-hints || true) && \
docker build -t smart-word-hints smart-word-hints-api/ && \
docker run --name smart-word-hints -p $PORT:8081 --rm -d smart-word-hints

echo "API available at http://localhost:$PORT/"