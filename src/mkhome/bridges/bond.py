import logging
import typing as _t

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from mkhome.utils import async_utils, requests
from mkhome.settings import settings


LOGGER = logging.getLogger(__name__)
BASE_URL = settings.bond_settings.bridge_url


DEVICE_TYPE = _t.Literal[
    "CF",  # Ceiling Fan
    "FP",  # Fireplace
    "MS",  # Motorized Window Coverings (Shades, Screens, Drapes) and Awnings
    "GX",  # Generic Device
    "LT",  # Light
    "BD",  # Bidet
]

DEVICE_SUB_TYPE = _t.Literal[
    "ROLLER",  # A roller blackout shade which blocks light and provides privacy
    "SHEER",  # A shade which permits light to pass and does not provide privacy
    "AWNING",  # An outdoor patio covering
]

DIRECTION = _t.Literal["FORWARD", "REVERSE"]


class BondBridgeAuth(requests.AuthBase):
    def __init__(self, token_url: str) -> None:
        self.token_url = token_url
        self.token: str | None = "09b9a6def7b0acde"

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        if self.token is None:
            res = async_utils.run_sync(requests.get(self.token_url))
            if not (200 <= res.status_code <= 299):
                raise HTTPException(res.status_code, res.text)
            data = res.json()
            if "token" not in data:
                raise HTTPException(res.status_code, data)
            self.token = data["token"]
        r.headers["BOND-Token"] = self.token  # type: ignore
        return r


class BondDevice(BaseModel):
    device_id: str
    name: str | None = None
    type: DEVICE_TYPE | None = None
    subtype: DEVICE_SUB_TYPE | None = None
    template: str | None = None
    location: str | None = None
    actions: list[str] = Field(default_factory=list)
    properties_hash: str | None = None
    state_hash: str | None = None
    device_hash: str | None = None
    commands_hash: str | None = None

    model_config = ConfigDict(extra="allow")

    @field_validator("properties_hash", "state_hash", "device_hash", "commands_hash", mode="before")
    @classmethod
    def parse_hash_value(cls, v: _t.Any):
        if isinstance(v, dict) and "_" in v:
            return v["_"]
        return None


class BondDeviceState(BaseModel):
    device_id: str
    power: bool | None = None
    timer: int | None = None
    speed: int | None = None
    light: int | None = None
    brightness: int | None = None
    breeze: list[int] = Field(default_factory=list)


class BondDeviceProperties(BaseModel):
    device_id: str
    addr: str = ""
    freq: int = 0
    zero_gap: int = 0
    bps: int = 0
    trust_state: bool = False
    max_speed: int = 0


def get_auth() -> requests.AuthBase:
    """Get an authentication object for Bond Bridge API requests.

    Returns:
        AuthBase: The generated authentication object
    """
    LOGGER.debug("Generating bond bridge authentication")
    return BondBridgeAuth(f"{BASE_URL}/v2/token")


async def startup() -> None:
    LOGGER.debug("Running Bond Bridge startup hook")


async def shutdown() -> None:
    LOGGER.debug("Running Bond Bridge shutdown hook")


async def get_devices() -> list[str]:
    """Get all devices attached to Bond Bridge

    Returns:
        list[str]: A list of device IDs for the Bond Bridge
    """
    endpoint = "/v2/devices"
    url = f"{BASE_URL}{endpoint}"
    LOGGER.debug("Request for %s", endpoint)
    res = await requests.get(url, auth=get_auth())
    if not (200 <= res.status_code <= 299):
        raise HTTPException(res.status_code, res.text)
    data = res.json()
    if not isinstance(data, dict):
        raise HTTPException(res.status_code, res.text)
    return [k for k in data.keys() if not k.startswith("_")]


async def get_device(device_id: str) -> BondDevice:
    """Retrieve the data for a device attached to the Bond Bridge by its `device_id`.

    Args:
        device_id (str): The ID of the device to retrieve

    Returns:
        BondBridgeDevice: The data for the retrieved Bond Bridge device
    """
    endpoint = f"/v2/devices/{device_id}"
    url = f"{BASE_URL}{endpoint}"
    LOGGER.debug("Request for %s", endpoint)
    res = await requests.get(url, auth=get_auth())
    if not (200 <= res.status_code <= 299):
        raise HTTPException(res.status_code, res.text)
    data = res.json()
    if not isinstance(data, dict):
        raise HTTPException(res.status_code, res.text)
    return BondDevice.model_validate({**data, "device_id": device_id})


async def get_state(device_id: str) -> BondDeviceState:
    endpoint = f"/v2/devices/{device_id}/state"
    url = f"{BASE_URL}{endpoint}"
    LOGGER.debug("Request for %s", endpoint)
    res = await requests.get(url, auth=get_auth())
    if not (200 <= res.status_code <= 299):
        raise HTTPException(res.status_code, res.text)
    data = res.json()
    if not isinstance(data, dict):
        raise HTTPException(res.status_code, res.text)
    state = BondDeviceState.model_validate({**data, "device_id": device_id})
    LOGGER.debug("Device state: %s", state.model_dump_json(indent=4))
    return state


async def get_properties(device_id: str) -> BondDeviceProperties:
    endpoint = f"/v2/devices/{device_id}/properties"
    url = f"{BASE_URL}{endpoint}"
    LOGGER.debug("Request for %s", endpoint)
    res = await requests.get(url, auth=get_auth())
    if not (200 <= res.status_code <= 299):
        raise HTTPException(res.status_code, res.text)
    data = res.json()
    if not isinstance(data, dict):
        raise HTTPException(res.status_code, res.text)
    props = BondDeviceProperties.model_validate({**data, "device_id": device_id})
    LOGGER.debug("Device properties: %s", props.model_dump_json(indent=4))
    return props


async def update_state(device_id: str, **payload) -> None:
    endpoint = f"/v2/devices/{device_id}/state"
    url = f"{BASE_URL}{endpoint}"
    LOGGER.debug("Request for %s with payload %s", endpoint, payload)
    res = await requests.patch(url, json=payload, auth=get_auth())
    LOGGER.debug("[%s] %s", res.status_code, res.text)
    if not (200 <= res.status_code <= 299):
        raise HTTPException(res.status_code, res.text)


async def execute_action(device_id: str, action: str, **payload: _t.Any) -> None:
    endpoint = f"/v2/devices/{device_id}/actions/{action}"
    url = f"{BASE_URL}{endpoint}"
    LOGGER.debug("Request for %s with payload %s", endpoint, payload)

    res = await requests.put(url, json=payload, auth=get_auth())
    try:
        body = res.json()
    except Exception:
        body = res.text
    LOGGER.debug("[%s] %s", res.status_code, body)
    if not (200 <= res.status_code <= 299):
        raise HTTPException(res.status_code, body)


async def power_on(device_id: str) -> None:
    await execute_action(device_id, "TurnOn")


async def power_off(device_id: str) -> None:
    await execute_action(device_id, "TurnOff")


async def toggle_power(device_id: str) -> None:
    await execute_action(device_id, "TogglePower")


async def set_timer(device_id: str, duration: int | None) -> None:
    await execute_action(device_id, "SetTimer", s=0 if duration is None else duration)


async def set_speed(device_id: str, speed: int) -> None:
    await execute_action(device_id, "SetSpeed", argument=speed)


async def increase_speed(device_id: str, step: int) -> None:
    await execute_action(device_id, "IncreaseSpeed", argument=step)


async def decrease_speed(device_id: str, step: int) -> None:
    state = await get_state(device_id)
    if state.speed == 1:
        return await power_off(device_id)
    await execute_action(device_id, "DecreaseSpeed", argument=step)


async def breeze_on(device_id: str) -> None:
    await execute_action(device_id, "BreezeOn")


async def breeze_off(device_id: str) -> None:
    await execute_action(device_id, "BreezeOff")


async def set_breeze(device_id: str, enabled: bool, mean: int, var: int) -> None:
    await execute_action(device_id, "SetBreeze", mode=int(enabled), mean=mean, var=var)


async def set_direction(device_id: str, direction: DIRECTION) -> None:
    await execute_action(device_id, "SetDirection", direction=1 if direction == "FORWARD" else -1)


async def toggle_direction(device_id: str) -> None:
    await execute_action(device_id, "ToggleDirection")


async def light_on(device_id: str) -> None:
    state = await get_state(device_id)
    if state.light == 1:
        return
    await execute_action(device_id, "TurnLightOn")


async def light_off(device_id: str) -> None:
    state = await get_state(device_id)
    if state.light == 0:
        return
    await execute_action(device_id, "TurnLightOff")


async def toggle_light(device_id: str) -> None:
    await execute_action(device_id, "ToggleLight")


async def set_light_belief_state(device_id: str, light: int) -> None:
    await update_state(device_id, light=light)


async def toggle_light_belief_state(device_id: str) -> None:
    state = await get_state(device_id)
    await update_state(device_id, light=int(not bool(state.light)))


async def set_brightness(device_id: str, brightness: int) -> None:
    if brightness == 0:
        return await light_off(device_id)
    await execute_action(device_id, "SetBrightness", argument=brightness)


async def increase_brightness(device_id: str, amount: int) -> None:
    await execute_action(device_id, "IncreaseBrightness", argument=amount)


async def decrease_brightness(device_id: str, amount: int) -> None:
    await execute_action(device_id, "DecreaseBrightness", argument=amount)


async def dim_mode(device_id: str) -> None:
    await execute_action(device_id, "DimMode")
