#!/bin/sh

cd smart_word_hints_api/requirements && \
pip-compile && \
pip-compile dev_requirements.in
