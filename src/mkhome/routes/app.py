import logging
import os
import subprocess
import threading
import time

from fastapi import BackgroundTasks, APIRouter, HTTPException


LOGGER = logging.getLogger(__name__)
ROUTER = APIRouter(prefix="/app")


def restart() -> None:
    cmd = [
        ".venv/bin/python3",
        "-m",
        "uvicorn",
        "mkhome:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8582",
        "--log-config",
        "config/logging.yaml",
        "--log-level",
        "info",
    ]
    os.execvp(cmd[0], cmd)


@ROUTER.get("/update", status_code=202, tags=["Application"])
async def update_application(background_tasks: BackgroundTasks) -> None:
    try:
        subprocess.run(["git", "checkout", "main"])
        time.sleep(1)
        subprocess.run(["git", "pull", "origin", "main"])
        time.sleep(1)
        background_tasks.add_task(restart)
    except Exception:
        LOGGER.exception("Failed to update application")
        raise HTTPException(500, "Internal service error")


@ROUTER.get("/restart", status_code=202, tags=["Application"])
async def restart_application() -> None:
    """Restarts this application"""
    try:
        t = threading.Thread(target=restart, daemon=False)
        t.start()
    except Exception:
        LOGGER.exception("Failed to restart application")
        raise HTTPException(500, "Internal service error")
