"""FastAPI backend for commerce event generation."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from gen_event.producer.event_service import build_page_view_event, build_purchase_event, build_random_events
from gen_event.storage.postgres import insert_event, insert_events


app = FastAPI(title="Commerce Event API")


class RandomEventRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100)


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
