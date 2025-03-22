#!/bin/bash
set -e

# Create data directory if it doesn't exist
echo "Creating data directory if it doesn't exist..."
mkdir -p ./data

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 