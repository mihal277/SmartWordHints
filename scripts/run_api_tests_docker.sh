#!/bin/sh

set -e

docker build -t smart_word_hints_tests -f tests.Dockerfile .
docker run --name smart_word_hints_tests --rm smart_word_hints_tests
