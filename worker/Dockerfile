FROM python:3.11-slim-buster

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

WORKDIR /app

COPY . worker

RUN pip install -r worker/requirements.txt

RUN python -m worker.startup

CMD ["/bin/bash", "worker/run.sh"]