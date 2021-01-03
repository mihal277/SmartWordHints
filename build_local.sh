#!/bin/bash

(docker stop smart-word-hints || true) && \
docker build -t smart-word-hints smart-word-hints-api/ && \
docker run --name smart-word-hints -p 8081:8081 --rm -d smart-word-hints