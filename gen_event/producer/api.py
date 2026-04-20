"""FastAPI backend for commerce event generation."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from gen_event.config.settings import get_settings
from gen_event.producer.event_service import build_page_view_event, build_purchase_event, build_random_events
from gen_event.storage.postgres import count_events, insert_event, insert_events, wait_for_connection


def _seed_events_once() -> None:
    settings = get_settings()
    batch_size = int(settings["auto_generate_batch_size"])

    wait_for_connection()
    if count_events() > 0:
        print("event_logs already contains data, skipping startup seed")
        return

    events = build_random_events(batch_size)
    insert_events(events)
    print(f"seeded {len(events)} events into PostgreSQL")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()

    if bool(settings["auto_generate_enabled"]):
        _seed_events_once()

    try:
        yield
    finally:
        return


app = FastAPI(title="Commerce Event API", lifespan=lifespan)


class RandomEventRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=500)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/events/page-view")
def create_page_view() -> dict:
    event = build_page_view_event()
    insert_event(event)
    return {"message": "page_view event created", "event": event}


@app.post("/events/purchase")
def create_purchase() -> dict:
    event = build_purchase_event()
    insert_event(event)
    return {"message": "purchase event created", "event": event}


@app.post("/events/random")
def create_random_events(request: RandomEventRequest) -> dict:
    events = build_random_events(request.count)
    insert_events(events)
    return {
        "message": f"{request.count} events created",
        "count": request.count,
        "events": events,
    }
