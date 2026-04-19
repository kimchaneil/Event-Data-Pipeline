"""PostgreSQL connection helpers for gen_event."""

from __future__ import annotations

from datetime import datetime
from psycopg import connect
from psycopg.connection import Connection
import uuid

from gen_event.config.settings import get_settings


def build_dsn() -> str:
    settings = get_settings()
    return (
        f"host={settings['postgres_host']} "
        f"port={settings['postgres_port']} "
        f"dbname={settings['postgres_db']} "
        f"user={settings['postgres_user']} "
        f"password={settings['postgres_password']}"
    )


def get_connection() -> Connection:
    return connect(build_dsn())


def insert_event(event: dict) -> None:
    insert_events([event])


def insert_events(events: list[dict]) -> None:
    if not events:
        return

    settings = get_settings()
    query = f"""
        INSERT INTO {settings["postgres_table"]} (
            event_id,
            event_type,
            event_time,
            user_id,
            session_id,
            page_url,
            product_id,
            product_name,
            referrer,
            device_type,
            quantity,
            price,
            currency,
            payment_method
        ) VALUES (
            %(event_id)s,
            %(event_type)s,
            %(event_time)s,
            %(user_id)s,
            %(session_id)s,
            %(page_url)s,
            %(product_id)s,
            %(product_name)s,
            %(referrer)s,
            %(device_type)s,
            %(quantity)s,
            %(price)s,
            %(currency)s,
            %(payment_method)s
        )
    """

    rows = [_build_insert_row(event) for event in events]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, rows)
        connection.commit()


def _build_insert_row(event: dict) -> dict:
    return {
        "event_id": uuid.UUID(event["event_id"]),
        "event_type": event["event_type"],
        "event_time": datetime.fromisoformat(event["event_time"]),
        "user_id": event["user_id"],
        "session_id": event["session_id"],
        "page_url": event["page_url"],
        "product_id": event["product_id"],
        "product_name": event["product_name"],
        "referrer": event.get("referrer"),
        "device_type": event.get("device_type"),
        "quantity": event.get("quantity"),
        "price": event.get("price"),
        "currency": event.get("currency"),
        "payment_method": event.get("payment_method"),
    }
