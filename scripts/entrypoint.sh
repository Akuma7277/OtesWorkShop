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

# Build the Mini App frontend if Node.js is available and not already built
WEBAPP_DIR="/app/src/webapp"
DIST_DIR="$WEBAPP_DIR/dist"

if command -v node > /dev/null 2>&1; then
    if [ ! -d "$DIST_DIR" ] || [ ! -f "$DIST_DIR/index.html" ]; then
        echo "Building Mini App frontend..."
        cd "$WEBAPP_DIR"
        npm install --prefer-offline 2>/dev/null || npm install
        npm run build
        cd /app
    else
        echo "Mini App frontend already built, skipping..."
    fi
else
    echo "Node.js not found, skipping frontend build."
fi

# Determine API port — Railway injects PORT automatically
API_PORT="${PORT:-8000}"

# Log the public URL if available (set automatically by Railway)
if [ -n "$RAILWAY_PUBLIC_DOMAIN" ]; then
    echo "Mini App will be accessible at: https://$RAILWAY_PUBLIC_DOMAIN"
fi

echo "Starting Shopim API Server on port $API_PORT..."
poetry run uvicorn src.shopim.api:app --host 0.0.0.0 --port "$API_PORT" --workers 1 &
API_PID=$!

echo "Starting Shopim Telegram Bot..."
poetry run python -m src.shopim.bot &
BOT_PID=$!

# Wait for either process to exit
wait $BOT_PID $API_PID
