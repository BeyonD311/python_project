#!/usr/bin/env sh
celery -A worker.celery_app worker -l info &
celery -A worker.celery_app beat -l info &
uvicorn main:app --reload --host '0.0.0.0'