"""Entrypoint for running the FastAPI backend."""

from __future__ import annotations

import uvicorn

from gen_event.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "gen_event.producer.api:app",
        host=str(settings["api_host"]),
        port=int(settings["api_port"]),
        reload=False,
    )


if __name__ == "__main__":
    main()
