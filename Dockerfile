FROM python:3.8

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

EXPOSE 80

COPY ./app /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]