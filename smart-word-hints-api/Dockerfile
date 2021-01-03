FROM tiangolo/uvicorn-gunicorn:python3.8

RUN useradd --create-home -u 5002 smart-word-hints-api
USER smart-word-hints-api

ENV PORT=8081

COPY requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

COPY nltk_modules.txt /tmp/
RUN python -m nltk.downloader $(cat /tmp/nltk_modules.txt)

COPY ./app /app