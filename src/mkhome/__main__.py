import asyncio
import contextlib
import logging
import os

from fastapi import FastAPI

from mkhome import bridges, routes
from mkhome.settings import settings
import mkhome.events


LOGGER = logging.getLogger(__name__)


### Lifecycle


async def startup(_: FastAPI) -> None:
    LOGGER.debug("Running startup hooks")
    await asyncio.gather(
        bridges.bond.startup(),
        bridges.lutron.startup(),
    )
    await mkhome.events.startup()
    LOGGER.debug("Startup hooks complete")


async def shutdown(_: FastAPI) -> None:
    LOGGER.debug("Running shutdown hooks")
    await asyncio.gather(
        bridges.bond.shutdown(),
        bridges.lutron.shutdown(),
    )
    await mkhome.events.shutdown()
    LOGGER.debug("Shutdown hooks complete")


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    await startup(_)
    yield
    ppid = os.getppid()
    msg = "Application shutdown started. Use pid %s to manually kill process"
    LOGGER.warning(msg, ppid)
    await shutdown(_)


### Application


app = FastAPI(
    debug=settings.application_settings.debug,
    title=settings.application_settings.title,
    summary=settings.application_settings.summary,
    description=settings.application_settings.description,
    version=settings.application_settings.version,
    lifespan=lifespan,
)
app.include_router(routes.bond.ROUTER)
app.include_router(routes.lutron.ROUTER)
