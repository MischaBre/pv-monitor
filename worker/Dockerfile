FROM python:3.11-slim-buster

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

WORKDIR /app

COPY worker worker
COPY requirements.txt .
COPY devices.json .

RUN pip install -r requirements.txt

COPY .env .

CMD ["python", "-m", "worker.run"]