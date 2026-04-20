"""Generate visualization images from PostgreSQL aggregate queries."""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from gen_event.config.settings import get_settings
from gen_event.storage.postgres import count_events, get_connection, wait_for_connection
from visual.sql_queries import (
    HOURLY_DISTRIBUTION_QUERY,
    PRODUCT_PERFORMANCE_QUERY,
    REFERRER_PERFORMANCE_QUERY,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def fetch_rows(query: str) -> list[dict]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column.name for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def wait_for_seeded_events() -> None:
    settings = get_settings()
    attempts = int(settings["postgres_connect_retries"])
    delay = int(settings["postgres_connect_retry_seconds"])

    wait_for_connection(max_attempts=attempts, delay_seconds=delay)

    for attempt in range(1, attempts + 1):
        if count_events() > 0:
            return
        if attempt == attempts:
            raise RuntimeError("event_logs is empty, visualization cannot be generated yet")
        time.sleep(delay)


def save_product_chart(rows: list[dict], output_dir: Path) -> Path:
    labels = [str(row["product_name"] or row["product_id"]) for row in rows]
    page_views = [int(row["page_view_count"]) for row in rows]
    purchases = [int(row["purchase_count"]) for row in rows]

    fig, ax = plt.subplots(figsize=(12, 6))
    positions = range(len(labels))
    width = 0.38

    ax.bar([pos - width / 2 for pos in positions], page_views, width=width, label="Page View", color="#1f77b4")
    ax.bar([pos + width / 2 for pos in positions], purchases, width=width, label="Purchase", color="#ff7f0e")
    ax.set_title("Product Performance")
    ax.set_ylabel("Event Count")
    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output_path = output_dir / "product_performance.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def save_referrer_chart(rows: list[dict], output_dir: Path) -> Path:
    labels = [str(row["referrer"]).title() for row in rows]
    conversion_rates = [float(row["conversion_rate_percent"]) for row in rows]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, conversion_rates, color="#2ca02c")
    ax.set_title("Referrer Conversion Rate")
    ax.set_ylabel("Conversion Rate (%)")
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, conversion_rates):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.3, f"{value:.2f}%", ha="center", va="bottom")

    fig.tight_layout()
    output_path = output_dir / "referrer_conversion_rate.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def save_hourly_chart(rows: list[dict], output_dir: Path) -> Path:
    hours = [int(row["event_hour"]) for row in rows]
    page_views = [int(row["page_view_count"]) for row in rows]
    purchases = [int(row["purchase_count"]) for row in rows]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(hours, page_views, marker="o", linewidth=2, label="Page View", color="#1f77b4")
    ax.plot(hours, purchases, marker="o", linewidth=2, label="Purchase", color="#d62728")
    ax.set_title("Hourly Event Distribution")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Event Count")
    ax.set_xticks(hours)
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()

    output_path = output_dir / "hourly_event_distribution.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    wait_for_seeded_events()
    output_dir = ensure_output_dir()
    product_rows = fetch_rows(PRODUCT_PERFORMANCE_QUERY)
    referrer_rows = fetch_rows(REFERRER_PERFORMANCE_QUERY)
    hourly_rows = fetch_rows(HOURLY_DISTRIBUTION_QUERY)

    saved_paths = [
        save_product_chart(product_rows, output_dir),
        save_referrer_chart(referrer_rows, output_dir),
        save_hourly_chart(hourly_rows, output_dir),
    ]

    for path in saved_paths:
        print(path)


if __name__ == "__main__":
    main()
