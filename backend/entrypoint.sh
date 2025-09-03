#!/bin/sh
set -e

# Wait for the database to be ready
# This is a simple loop, a more robust solution would use a tool like wait-for-it.sh
# For now, this is enough to avoid race conditions on startup
sleep 5

echo "--- Running Alembic migrations ---"
alembic upgrade head
echo "--- Alembic migrations finished ---"

# Start the application
exec python run.py
