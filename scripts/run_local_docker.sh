#!/bin/sh

DEFAULTPORT=8081
PORT="${1:-$DEFAULTPORT}"

(docker stop smart_word_hints || true) && \
docker build -t smart_word_hints smart_word_hints_api/ && \
docker run --name smart_word_hints -p $PORT:8081 --rm -d smart_word_hints

echo "API available at http://localhost:$PORT/"