# Shopim Telegram Bot

This is a Telegram bot for managing sales, inventory, and users for a shop, as per the technical specification.

## 🚧 Work in Progress 🚧

This project is currently under construction by a Gemini AI agent.

## Setup and Installation

_(Instructions will be added here once the initial development is complete.)_

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd shopim-bot
    ```

2.  **Create and configure the environment:**
    ```bash
    cp .env.example .env
    ```
    -   Edit the `.env` file with your actual `BOT_TOKEN`, `SUPER_ADMIN_IDS`, and a strong `POSTGRES_PASSWORD`.

3.  **Run the application:**
    ```bash
    docker compose up --build
    ```

## Usage

-   Find your bot on Telegram and send the `/start` command.
-   If you are a super admin, you should see the admin keyboard.

## Migrations

To create a new migration:
```bash
docker compose run --rm bot poetry run alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:
```bash
docker compose run --rm bot poetry run alembic upgrade head
```

## Seeding Admin

After the services are running, you need to create a super admin to manage the bot.

1.  Find your Telegram User ID (e.g., by sending a message to `@userinfobot`).
2.  Run the following command, replacing the placeholders:

```bash
docker compose run --rm bot poetry run python scripts/seed_admin.py <YOUR_TELEGRAM_ID> "Your Full Name"
```

For example:
```bash
docker compose run --rm bot poetry run python scripts/seed_admin.py 123456789 "John Doe"
```

This will create a `SUPER_ADMIN` in the database. You can now use the bot as an administrator.
