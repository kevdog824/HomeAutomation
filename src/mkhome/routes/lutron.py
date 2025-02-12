import logging

from fastapi import APIRouter, HTTPException

from mkhome.bridges import lutron


LOGGER = logging.getLogger(__name__)
ROUTER = APIRouter(prefix="/lutron")


### Devices


@ROUTER.get("/devices", tags=["Lutron"])
async def get_devices() -> list[lutron.LutronDevice]:
    try:
        return await lutron.get_devices()
    except HTTPException:
        LOGGER.exception("Failed to retrieve Lutron devices")
        raise
    except Exception:
        LOGGER.exception("Failed to retrieve Lutron devices")
        raise HTTPException(500, "Internal service error")


@ROUTER.get("/devices/{device_id}", tags=["Lutron"])
async def get_device(device_id: str) -> lutron.LutronDevice:
    try:
        return await lutron.get_device(device_id)
    except HTTPException:
        LOGGER.exception("Failed to retrieve Lutron device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to retrieve Lutron device %s", device_id)
        raise HTTPException(500, "Internal service error")


### Switches


@ROUTER.get("/devices/{device_id}/on", tags=["Lutron"])
async def turn_on_device(device_id: str) -> None:
    try:
        return await lutron.turn_on_device(device_id)
    except HTTPException:
        LOGGER.exception("Failed to turn on Lutron switch %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to turn on Lutron switch %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.get("/devices/{device_id}/off", tags=["Lutron"])
async def turn_off_switch(device_id: str) -> None:
    try:
        return await lutron.turn_off_device(device_id)
    except HTTPException:
        LOGGER.exception("Failed to turn off Lutron switch %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to turn off Lutron switch %s", device_id)
        raise HTTPException(500, "Internal service error")


### Buttons


@ROUTER.get("/buttons/", tags=["Lutron"])
async def get_buttons() -> list[lutron.LutronButton]:
    try:
        return await lutron.get_buttons()
    except HTTPException:
        LOGGER.exception("Failed to retrieve Lutron buttons")
        raise
    except Exception:
        LOGGER.exception("Failed to retrieve Lutron buttons")
        raise HTTPException(500, "Internal service error")


@ROUTER.get("/buttons/{button_id}/tap", tags=["Lutron"])
async def tap_button(button_id: str) -> None:
    try:
        return await lutron.tap_button(button_id)
    except HTTPException:
        LOGGER.exception("Failed to tap Lutron button %s", button_id)
        raise
    except Exception:
        LOGGER.exception("Failed to tap Lutron button %s", button_id)
        raise HTTPException(500, "Internal service error")
