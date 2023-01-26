FROM python:3.10.8-alpine

# RUN adduser -D app-python
# USER app-python

WORKDIR /app

RUN apk update && \ 
apk add --virtual build-deps gcc python3-dev musl-dev && \
apk add postgresql-dev

# COPY --chown=app-python:app-python . .

COPY . .

RUN python -m pip install --upgrade pip && \
pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location --requirement  requirements.txt

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]