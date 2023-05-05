FROM python:3.10.8-alpine

RUN apk update && \
apk add --virtual build-deps gcc python3-dev musl-dev && \
apk add postgresql-dev

COPY requirements.txt /
RUN python -m pip install --upgrade pip && \
pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location --requirement  requirements.txt
RUN pip install redis
RUN pip install --no-cache-dir flower

WORKDIR /app
COPY . /app

CMD celery -A worker.celery_app worker -l info


