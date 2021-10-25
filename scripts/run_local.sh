#!/bin/sh

uvicorn smart_word_hints_api.app.main:app --reload --port 8081