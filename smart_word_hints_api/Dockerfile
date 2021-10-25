FROM tiangolo/uvicorn-gunicorn:python3.9-slim-2021-10-02

RUN useradd --create-home -u 5002 smart_word_hints_api
USER smart_word_hints_api

ENV PORT=8081
ENV MODULE_NAME=smart_word_hints_api.app.main

COPY requirements/requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

COPY requirements/nltk_modules.txt /tmp/
RUN python -m nltk.downloader $(cat /tmp/nltk_modules.txt)

COPY ./app /app/smart_word_hints_api/app
COPY ./__init__.py /app/smart_word_hints_api/__init__.py