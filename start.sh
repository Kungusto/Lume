#!/bin/sh
alembic upgrade head
exec python src/main.py
