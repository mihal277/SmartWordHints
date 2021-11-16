#!/bin/sh

set -e

echo "----- Running python tests -----"

echo "----- Running flake8 - Python linter -----"
flake8 smart_word_hints_api

echo "----- Running black - Python code formatter -----"
black smart_word_hints_api --check

echo "----- Running isort - utility to sort imports -----"
isort smart_word_hints_api --check

echo "----- Running mypy - static type checker -----"
mypy smart_word_hints_api

echo "----- Running pytest -----"
pytest smart_word_hints_api