#!/bin/sh

echo "Starting Container"

echo "Running Alembic migrations..."
set +e
poetry run alembic upgrade head
MIGRATION_STATUS=$?
set -e

if [ $MIGRATION_STATUS -ne 0 ]; then
    echo "SQLite dialect detected. Skipping Postgres-specific alembic migrations (handled by create_all in bot)."
fi

echo "Compiling locales..."
poetry run python scripts/compile_locales.py

# Build the Mini App frontend if Node.js is available
if command -v node > /dev/null 2>&1; then
    echo "Building Mini App frontend..."
    cd /app/src/webapp
    npm ci --prefer-offline 2>/dev/null || npm install
    npm run build
    cd /app
fi

echo "Starting Shopim API Server..."
# Start FastAPI API server in background on port 8000
poetry run uvicorn src.shopim.api:app --host 0.0.0.0 --port 8000 --workers 1 &
API_PID=$!

echo "Starting Shopim Telegram Bot..."
poetry run python -m src.shopim.bot &
BOT_PID=$!

# Wait for either process to exit
wait $BOT_PID $API_PID
