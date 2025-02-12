import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mkhome.bridges import bond


LOGGER = logging.getLogger(__name__)
ROUTER = APIRouter(prefix="/bond")


class SetBreezeRequest(BaseModel):
    enabled: bool
    """Whether breeze mode should be turned on or off by this request."""
    mean: int = Field(50, ge=0, le=100)
    """Average fan speed for breeze mode"""
    var: int = Field(50, ge=0, le=100)
    """Variability of fan speed for breeze mode"""


@ROUTER.get("/devices", tags=["Bond"])
async def get_devices() -> list[str]:
    """Get all devices attached to Bond Bridge

    return awaits:
        list[str]: A list of device IDs for the Bond Bridge
    """
    try:
        return await bond.get_devices()
    except HTTPException:
        LOGGER.exception("Failed to retrieve Bond Bridge devices")
        raise
    except Exception:
        LOGGER.exception("Failed to retrieve Bond Bridge devices")
        raise HTTPException(500, "Internal service error")


@ROUTER.get("/devices/{device_id}", tags=["Bond"])
async def get_device(device_id: str) -> bond.BondDevice:
    """Retrieve the data for a device attached to the Bond Bridge by its `device_id`.

    Args:
        device_id (str): The ID of the device to retrieve

    return awaits:
        BondDevice: The data for the retrieved Bond Bridge device
    """
    try:
        return await bond.get_device(device_id)
    except HTTPException as exc:
        LOGGER.exception("Failed to retrieve Bond Bridge device %s", device_id)
        if exc.status_code == 404:
            raise HTTPException(404, f"Bond Bridge device {device_id} not found") from None
        raise
    except Exception:
        LOGGER.exception("Failed to retrieve Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.get("/devices/{device_id}/state", tags=["Bond"])
async def get_state(device_id: str) -> bond.BondDeviceState:
    try:
        return await bond.get_state(device_id)
    except HTTPException:
        LOGGER.exception("Failed to retrieve state of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to retrieve state of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/power-on", tags=["Bond"])
async def power_on(device_id: str) -> None:
    try:
        return await bond.power_on(device_id)
    except HTTPException:
        LOGGER.exception("Failed to power on Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to power on Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/power-on", tags=["Bond"])
async def power_off(device_id: str) -> None:
    try:
        return await bond.power_off(device_id)
    except HTTPException:
        LOGGER.exception("Failed to power off Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to power off Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/toggle-power", tags=["Bond"])
async def toggle_power(device_id: str) -> None:
    try:
        return await bond.toggle_power(device_id)
    except HTTPException:
        LOGGER.exception("Failed to toggle power for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to toggle power for Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/set-timer/{duration}", tags=["Bond"])
async def set_timer(device_id: str, duration: int | None) -> None:
    try:
        return await bond.set_timer(device_id, duration)
    except HTTPException:
        LOGGER.exception("Failed to set timer for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to set timer for Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/set-speed/{speed}", tags=["Bond"])
async def set_speed(device_id: str, speed: int) -> None:
    try:
        return await bond.set_speed(device_id, speed)
    except HTTPException:
        LOGGER.exception("Failed to set speed of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to set speed of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/increase-speed/{step}", tags=["Bond"])
async def increase_speed(device_id: str, step: int) -> None:
    try:
        return await bond.increase_speed(device_id, step)
    except HTTPException:
        LOGGER.exception("Failed to increase speed of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to increase speed of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/decrease-speed/{step}", tags=["Bond"])
async def decrease_speed(device_id: str, step: int) -> None:
    try:
        return await bond.decrease_speed(device_id, step)
    except HTTPException:
        LOGGER.exception("Failed to decrease speed of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to decrease speed of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/breeze-on", tags=["Bond"])
async def breeze_on(device_id: str) -> None:
    try:
        return await bond.breeze_on(device_id)
    except HTTPException:
        LOGGER.exception("Failed to turn on breeze for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to turn on breeze for Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/breeze-off", tags=["Bond"])
async def breeze_off(device_id: str) -> None:
    try:
        return await bond.breeze_off(device_id)
    except HTTPException:
        LOGGER.exception("Failed to turn off breeze for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to turn off breeze for Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/set-breeze", tags=["Bond"])
async def set_breeze(device_id: str, req: SetBreezeRequest) -> None:
    try:
        return await bond.set_breeze(device_id, req.enabled, req.mean, req.var)
    except HTTPException:
        LOGGER.exception("Failed to set breeze for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to set breeze for Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/set-direction/{direction}", tags=["Bond"])
async def set_direction(device_id: str, direction: bond.DIRECTION) -> None:
    try:
        return await bond.set_direction(device_id, direction)
    except HTTPException:
        LOGGER.exception("Failed to set direction of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to set direction of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/toggle-direction", tags=["Bond"])
async def toggle_direction(device_id: str) -> None:
    try:
        return await bond.toggle_direction(device_id)
    except HTTPException:
        LOGGER.exception("Failed to toggle direction of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to toggle direction of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/light-on", tags=["Bond"])
async def light_on(device_id: str) -> None:
    try:
        return await bond.light_on(device_id)
    except HTTPException:
        LOGGER.exception("Failed to turn light on for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to turn light on for Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/light-on", tags=["Bond"])
async def light_off(device_id: str) -> None:
    try:
        return await bond.light_off(device_id)
    except HTTPException:
        LOGGER.exception("Failed to turn light on for Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to turn light on for Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/toggle-light", tags=["Bond"])
async def toggle_light(device_id: str) -> None:
    try:
        return await bond.toggle_light(device_id)
    except HTTPException:
        LOGGER.exception("Failed to toggle light of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to toggle light of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/set-brightness/{brightness}", tags=["Bond"])
async def set_brightness(device_id: str, brightness: int) -> None:
    try:
        return await bond.set_brightness(device_id, brightness)
    except HTTPException:
        LOGGER.exception("Failed to set brightness of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to set brightness of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/increase-brightness/{amount}", tags=["Bond"])
async def increase_brightness(device_id: str, amount: int) -> None:
    try:
        return await bond.increase_brightness(device_id, amount)
    except HTTPException:
        LOGGER.exception("Failed to increase brightness of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to increase brightness of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")


@ROUTER.put("/devices/{device_id}/decrease-brightness/{amount}", tags=["Bond"])
async def decrease_brightness(device_id: str, amount: int) -> None:
    try:
        return await bond.decrease_brightness(device_id, amount)
    except HTTPException:
        LOGGER.exception("Failed to decrease brightness of Bond Bridge device %s", device_id)
        raise
    except Exception:
        LOGGER.exception("Failed to decrease brightness of Bond Bridge device %s", device_id)
        raise HTTPException(500, "Internal service error")
