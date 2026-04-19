"""PostgreSQL connection helpers for gen_event."""

from __future__ import annotations

from psycopg import connect
from psycopg.connection import Connection

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
