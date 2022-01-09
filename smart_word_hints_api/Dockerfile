FROM tiangolo/uvicorn-gunicorn:python3.9-slim-2021-10-02

RUN useradd --create-home -u 5002 smart_word_hints_api
USER smart_word_hints_api

ENV PORT=8081
ENV MODULE_NAME=smart_word_hints_api.app.main

COPY requirements/requirements.txt /tmp/
COPY requirements/nltk_modules.txt /tmp/
COPY requirements/spacy_modules.txt /tmp/

RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

RUN python -m nltk.downloader $(cat /tmp/nltk_modules.txt)
RUN python -m spacy download $(cat /tmp/spacy_modules.txt)

COPY ./app /app/smart_word_hints_api/app
COPY ./config.ini /app/smart_word_hints_api/config.ini
COPY ./__init__.py /app/smart_word_hints_api/__init__.py