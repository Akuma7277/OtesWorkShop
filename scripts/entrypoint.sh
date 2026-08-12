#!/bin/sh
set -e

echo "Checking Database configuration..."
if [ -z "$DATABASE_URL" ] && [ -z "$DATABASE_PUBLIC_URL" ] && [ -z "$POSTGRES_HOST" ] && [ -z "$PGHOST" ]; then
    echo "=================================================================="
    echo "WARNING: Database connection variable is not set!"
    echo "Please add DATABASE_URL in Railway Variables:"
    echo "DATABASE_URL = \${{Postgres.DATABASE_URL}}"
    echo "=================================================================="
fi

echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Starting Shopim Telegram Bot..."
poetry run python -m src.shopim.bot
