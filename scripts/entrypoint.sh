#!/bin/sh

echo "Running Alembic migrations..."
set +e
poetry run alembic upgrade head
MIGRATION_STATUS=$?
set -e

if [ $MIGRATION_STATUS -ne 0 ]; then
    echo "Notice: Alembic migration skipped or ended with warnings. Proceeding with bot startup..."
fi

echo "Starting Shopim Telegram Bot..."
poetry run python -m src.shopim.bot
