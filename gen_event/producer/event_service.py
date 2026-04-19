"""Commerce event generation and persistence helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import random
import uuid


PRODUCTS = [
    {"product_id": "SKU-1001", "product_name": "Classic White T-Shirt", "price": 29.0},
    {"product_id": "SKU-1002", "product_name": "Daily Denim Pants", "price": 59.0},
    {"product_id": "SKU-1003", "product_name": "Running Sneakers", "price": 129.0},
]

USERS = ["user-101", "user-102", "user-103", "user-104"]
REFERRERS = ["direct", "search", "email", "social"]
DEVICES = ["mobile", "desktop", "tablet"]
PAYMENT_METHODS = ["card", "bank_transfer", "simple_pay"]


def build_page_view_event() -> dict:
    product = random.choice(PRODUCTS)
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "page_view",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "user_id": random.choice(USERS),
        "session_id": f"session-{random.randint(10000, 99999)}",
        "page_url": f"/products/{product['product_id']}",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "referrer": random.choice(REFERRERS),
        "device_type": random.choice(DEVICES),
    }


def build_purchase_event() -> dict:
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 3)
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "purchase",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "user_id": random.choice(USERS),
        "session_id": f"session-{random.randint(10000, 99999)}",
        "page_url": f"/checkout/{product['product_id']}",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "quantity": quantity,
        "price": product["price"],
        "currency": "KRW",
        "payment_method": random.choice(PAYMENT_METHODS),
    }


def build_random_events(count: int) -> list[dict]:
    events: list[dict] = []
    for _ in range(count):
        event_builder = random.choices(
            [build_page_view_event, build_purchase_event],
            weights=[7, 3],
            k=1,
        )[0]
        events.append(event_builder())
    return events


def append_events(log_path: str, events: list[dict]) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")
