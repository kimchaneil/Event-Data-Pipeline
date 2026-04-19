"""FastAPI backend for commerce event generation."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from gen_event.config.settings import get_settings
from gen_event.producer.event_service import append_events, build_page_view_event, build_purchase_event, build_random_events


app = FastAPI(title="Commerce Event API")


class RandomEventRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=100)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/events/page-view")
def create_page_view() -> dict:
    settings = get_settings()
    event = build_page_view_event()
    append_events(str(settings["event_log_path"]), [event])
    return {"message": "page_view event created", "event": event}


@app.post("/events/purchase")
def create_purchase() -> dict:
    settings = get_settings()
    event = build_purchase_event()
    append_events(str(settings["event_log_path"]), [event])
    return {"message": "purchase event created", "event": event}


@app.post("/events/random")
def create_random_events(request: RandomEventRequest) -> dict:
    settings = get_settings()
    events = build_random_events(request.count)
    append_events(str(settings["event_log_path"]), events)
    return {
        "message": f"{request.count} events created",
        "count": request.count,
        "events": events,
    }
