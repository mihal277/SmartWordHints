FROM tiangolo/uvicorn-gunicorn:python3.8


RUN useradd --create-home -u 5002 smart-word-hints-api
USER smart-word-hints-api

COPY requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

COPY ./app /app