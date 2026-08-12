# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# nc (netcat) is used in the docker-compose command to check for DB readiness
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    gettext && \
    rm -rf /var/lib/apt/lists/*

# Install poetry and database drivers
RUN pip install poetry asyncpg aiosqlite

# Copy only the files necessary for installing dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies
# --no-root is important to avoid installing the project itself as editable
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi --no-root

# Copy the rest of the application's source code
COPY . .

# Compile gettext translations for all locales (uz, ru)
RUN python scripts/compile_locales.py

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh

# Default command to run migrations and start the application
CMD ["sh", "/app/scripts/entrypoint.sh"]

