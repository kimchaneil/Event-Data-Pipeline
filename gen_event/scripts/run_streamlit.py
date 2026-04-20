"""Entrypoint for running the Streamlit frontend."""

from __future__ import annotations

import os
import subprocess
import sys

from gen_event.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    env = os.environ.copy()
    env["STREAMLIT_SERVER_ADDRESS"] = str(settings["streamlit_host"])
    env["STREAMLIT_SERVER_PORT"] = str(settings["streamlit_port"])
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "gen_event/visualization/app.py"],
        check=True,
        env=env,
    )


if __name__ == "__main__":
    main()
