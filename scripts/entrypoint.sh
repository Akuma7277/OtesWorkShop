#!/bin/sh
set -e

echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Starting Shopim Telegram Bot..."
poetry run python -m src.shopim.bot
