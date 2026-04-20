"""Commerce event generation and persistence helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random
import uuid


PRODUCTS = [
    {"product_id": "SKU-1001", "product_name": "Python Backend Bootcamp", "price": 79.0},
    {"product_id": "SKU-1002", "product_name": "SQL Analytics Starter", "price": 49.0},
    {"product_id": "SKU-1003", "product_name": "FastAPI Practical Project", "price": 89.0},
    {"product_id": "SKU-1004", "product_name": "Data Pipeline Masterclass", "price": 129.0},
    {"product_id": "SKU-1005", "product_name": "Streamlit Dashboard Lab", "price": 59.0},
]
PRODUCT_VIEW_WEIGHTS = {
    "SKU-1001": 5,
    "SKU-1002": 4,
    "SKU-1003": 3,
    "SKU-1004": 2,
    "SKU-1005": 4,
}
PRODUCT_PURCHASE_RATE_MULTIPLIERS = {
    "SKU-1001": 0.90,
    "SKU-1002": 0.70,
    "SKU-1003": 1.10,
    "SKU-1004": 1.45,
    "SKU-1005": 1.20,
}

USERS = ["user-101", "user-102", "user-103", "user-104"]
REFERRERS = ["direct", "search", "email", "social"]
REFERRER_VIEW_WEIGHTS = {
    "direct": 2,
    "search": 5,
    "email": 1,
    "social": 4,
}
REFERRER_PURCHASE_RATES = {
    "direct": 0.45,
    "search": 0.18,
    "email": 0.35,
    "social": 0.08,
}
DEVICES = ["mobile", "desktop", "tablet"]
PAYMENT_METHODS = ["card", "bank_transfer", "simple_pay"]
PEAK_HOURS = [12, 13, 20, 21, 22]
ACTIVE_HOURS = [9, 10, 11, 14, 15, 18, 19, 23]
QUIET_HOURS = [hour for hour in range(24) if hour not in PEAK_HOURS + ACTIVE_HOURS]


def build_event_time() -> str:
    now = datetime.now(timezone.utc)
    day_offset = random.randint(0, 6)
    event_date = now - timedelta(days=day_offset)
    event_hour = random.choices(
        population=[
            random.choice(PEAK_HOURS),
            random.choice(ACTIVE_HOURS),
            random.choice(QUIET_HOURS),
        ],
        weights=[6, 3, 1],
        k=1,
    )[0]
    event_minute = random.randint(0, 59)
    event_second = random.randint(0, 59)
    event_time = event_date.replace(
        hour=event_hour,
        minute=event_minute,
        second=event_second,
        microsecond=0,
    )
    return event_time.isoformat()


def choose_referrer() -> str:
    return random.choices(
        population=list(REFERRER_VIEW_WEIGHTS.keys()),
        weights=list(REFERRER_VIEW_WEIGHTS.values()),
        k=1,
    )[0]


def choose_product() -> dict:
    product_ids = [product["product_id"] for product in PRODUCTS]
    chosen_product_id = random.choices(
        population=product_ids,
        weights=[PRODUCT_VIEW_WEIGHTS[product_id] for product_id in product_ids],
        k=1,
    )[0]
    return next(product for product in PRODUCTS if product["product_id"] == chosen_product_id)


def build_page_view_event() -> dict:
    product = choose_product()
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "page_view",
        "event_time": build_event_time(),
        "user_id": random.choice(USERS),
        "session_id": f"session-{random.randint(10000, 99999)}",
        "page_url": f"/products/{product['product_id']}",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "referrer": choose_referrer(),
        "device_type": random.choice(DEVICES),
    }


def build_purchase_event(source_event: dict | None = None) -> dict:
    product = random.choice(PRODUCTS) if source_event is None else {
        "product_id": source_event["product_id"],
        "product_name": source_event["product_name"],
        "price": next(item["price"] for item in PRODUCTS if item["product_id"] == source_event["product_id"]),
    }
    quantity = random.randint(1, 3)
    event_time = build_event_time()
    user_id = random.choice(USERS)
    session_id = f"session-{random.randint(10000, 99999)}"

    if source_event is not None:
        event_time = build_purchase_time(source_event["event_time"])
        user_id = source_event["user_id"]
        session_id = source_event["session_id"]

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "purchase",
        "event_time": event_time,
        "user_id": user_id,
        "session_id": session_id,
        "page_url": f"/checkout/{product['product_id']}",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "quantity": quantity,
        "price": product["price"],
        "currency": "KRW",
        "payment_method": random.choice(PAYMENT_METHODS),
    }


def build_purchase_time(page_view_time: str) -> str:
    source_time = datetime.fromisoformat(page_view_time)
    delay_minutes = random.randint(5, 180)
    purchase_time = source_time + timedelta(minutes=delay_minutes)
    return purchase_time.isoformat()


def should_convert_to_purchase(page_view_event: dict) -> bool:
    referrer = page_view_event["referrer"]
    product_id = page_view_event["product_id"]
    purchase_rate = REFERRER_PURCHASE_RATES.get(referrer, 0.1)
    purchase_rate *= PRODUCT_PURCHASE_RATE_MULTIPLIERS.get(product_id, 1.0)
    purchase_rate = min(purchase_rate, 0.95)
    return random.random() < purchase_rate


def build_random_events(count: int) -> list[dict]:
    events: list[dict] = []
    while len(events) < count:
        page_view_event = build_page_view_event()
        events.append(page_view_event)
        if len(events) >= count:
            break

        if should_convert_to_purchase(page_view_event):
            events.append(build_purchase_event(page_view_event))
    return events


def append_events(log_path: str, events: list[dict]) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")
