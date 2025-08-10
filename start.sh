#!/bin/sh
mkdir -p /app/src/analytics/data
alembic upgrade head
exec python src/main.py
