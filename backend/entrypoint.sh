#!/bin/sh
set -e

if [ ! -f "/app/alembic/.initialized" ]; then
  echo "Running alembic revision --autogenerate..."
  cd /app
  alembic revision --autogenerate -m "Initial migration"
  alembic upgrade head
  touch /app/alembic/.initialized
else
  echo "Applying pending migrations..."
  cd /app
  alembic upgrade head
fi

echo "Starting API..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
