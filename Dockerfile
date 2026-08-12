# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies + Node.js LTS (for Mini App build)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    gettext \
    curl \
    ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install poetry and database drivers
RUN pip install poetry asyncpg aiosqlite

# Copy only the files necessary for installing dependencies
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi --no-root

# Copy the rest of the application's source code
COPY . .

# Build Mini App frontend
RUN cd /app/src/webapp && npm ci --prefer-offline 2>/dev/null || npm install && npm run build

# Compile gettext translations for all locales (uz, ru)
RUN python scripts/compile_locales.py

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh

# Expose API port
EXPOSE 8000

# Default command to run migrations and start the application
CMD ["sh", "/app/scripts/entrypoint.sh"]
