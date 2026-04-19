"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path


def get_settings() -> dict[str, str | int]:
    base_dir = Path(__file__).resolve().parent.parent
    return {
        "api_host": os.getenv("API_HOST", "127.0.0.1"),
        "api_port": int(os.getenv("API_PORT", "8000")),
        "streamlit_host": os.getenv("STREAMLIT_HOST", "127.0.0.1"),
        "streamlit_port": int(os.getenv("STREAMLIT_PORT", "8501")),
        "api_base_url": os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
        "postgres_host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "postgres_port": int(os.getenv("POSTGRES_PORT", "5432")),
        "postgres_db": os.getenv("POSTGRES_DB", "commerce_events"),
        "postgres_user": os.getenv("POSTGRES_USER", "commerce_admin"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD", "commerce_password"),
        "postgres_table": os.getenv("POSTGRES_TABLE", "event_logs"),
        "event_log_path": os.getenv("EVENT_LOG_PATH", str(base_dir / "data" / "events.jsonl")),
        "random_batch_size": int(os.getenv("RANDOM_BATCH_SIZE", "50")),
    }
