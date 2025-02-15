import logging
import os
import subprocess
import sys

from fastapi import APIRouter, HTTPException


LOGGER = logging.getLogger(__name__)
ROUTER = APIRouter(prefix="/app")


def restart() -> None:
    try:
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception:
        raise HTTPException(500, "Failed to restart application")


@ROUTER.get("/update", tags=["Application"])
async def update_application() -> None:
    subprocess.run("git checkout main")
    subprocess.run("git pull origin/main")
    restart()


@ROUTER.get("/restart", tags=["Application"])
async def restart_application() -> None:
    """Restarts this application"""
    try:
        restart()
    except Exception:
        LOGGER.exception("Failed to restart application")
        raise HTTPException(500, "Internal service error")
