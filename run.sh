!/usr/bin/sh
celery -A worker.celery_app worker -l DEBUG &
celery -A worker.celery_app beat -l DEBUG &

uvicorn main:app --reload --host '0.0.0.0'