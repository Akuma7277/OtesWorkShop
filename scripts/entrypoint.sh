#!/bin/sh
set -e

echo "Running Alembic migrations..."
poetry run alembic upgrade head || echo "Alembic migration warning, proceeding to start bot..."

echo "Starting Shopim Telegram Bot..."
poetry run python -m src.shopim.bot
