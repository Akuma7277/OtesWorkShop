import uuid
from datetime import datetime


def generate_order_number() -> str:
    """Generates a unique order number based on date and a UUID snippet."""
    now = datetime.utcnow()
    date_part = now.strftime("%Y%m%d")
    uuid_part = str(uuid.uuid4().hex)[:6].upper()
    return f"SH-{date_part}-{uuid_part}"