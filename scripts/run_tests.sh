#!/bin/sh

set -e

echo "----- Running black - Python code formatter -----"
black . --check

echo "----- Running isort - utility to sort imports -----"
isort . --profile black --check

echo "----- Running pytest -----"
pytest .