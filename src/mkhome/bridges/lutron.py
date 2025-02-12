import asyncio
import logging
import threading
import time
import typing as _t

from fastapi import HTTPException
from pydantic import BaseModel
from pylutron_caseta.smartbridge import Smartbridge

from mkhome.settings import settings


LOGGER = logging.getLogger(__name__)
BRIDGE = Smartbridge.create_tls(
    settings.lutron_settings.bridge_ip,
    settings.lutron_settings.client_key,
    settings.lutron_settings.client_certificate,
    settings.lutron_settings.bridge_certificate,
)


ButtonAction = _t.Literal["SINGLE_CLICK", "DOUBLE_CLICK", "LONG_PRESS"]


class LutronButtonListener(_t.Protocol):
    def __call__(self, button_id: str, action: ButtonAction, /) -> _t.Any: ...


@_t.final
class LutronButtonHandler:
    def __init__(self, button_id: str, listener: LutronButtonListener) -> None:
        self.button_id = button_id
        self.listener = listener
        self._long_press_duration = 1.0
        self._double_click_duration = 0.5
        self._long_press_task = None
        self._double_click_task = None
        self._click_time = 0
        self._click_count = 0
        self._lock = threading.Lock()

    def __str__(self) -> str:
        if hasattr(self.listener, "__str__"):
            name = str(self.listener)
        if hasattr(self.listener, "__name__"):
            name = self.listener.__name__  # type: ignore
        elif hasattr(self.listener, "__class__") and hasattr(self.listener.__class__, "__name__"):
            name = self.listener.__class__.__name__
        else:
            name = "UNKNOWN"
        return f"ButtonHandler<{name}>"

    def button_down_handler(self):
        with self._lock:
            self._click_time = time.time()
            self._click_count += 1
            self._long_press_task = threading.Timer(
                self._long_press_duration, self.long_press_handler
            )
            self._long_press_task.start()

    def button_up_handler(self):
        with self._lock:
            if self._click_count == 1:
                self._double_click_timer = threading.Timer(
                    self._double_click_duration, self.double_click_handler
                )
                self._double_click_timer.start()

            if self._long_press_task:
                self._long_press_task.cancel()
                self._long_press_task = None

    def long_press_handler(self):
        with self._lock:
            if time.time() - self._click_time >= self._long_press_duration:
                self.button_listener(self.button_id, "LONG_PRESS")
                self._click_count = 0
            self._long_press_task = None

    def double_click_handler(self):
        with self._lock:
            if self._click_count == 1:
                self.button_listener(self.button_id, "SINGLE_CLICK")
            elif self._click_count == 2:
                self.button_listener(self.button_id, "DOUBLE_CLICK")
            self._click_count = 0
            self._double_click_timer = None

    def button_listener(self, button_id: str, action: ButtonAction) -> _t.Any:
        LOGGER.info("Button Event: <%s | %s>", button_id, action)
        try:
            return self.listener(button_id, action)
        except BaseException:
            LOGGER.exception("Exception occurred in listener %s", self)
            return None

    def __call__(self, state: str) -> None:
        match state:
            case "Press":
                self.button_down_handler()
            case "Release":
                self.button_up_handler()


class LutronDevice(BaseModel):
    device_id: int
    current_state: int | str
    fan_speed: _t.Any = None
    tilt: _t.Any = None
    zone: int | None = None
    name: str | None = None
    button_groups: list[str] | None = None
    occupancy_sensors: _t.Any = None
    type: str | None = None
    model: str | None = None
    serial: str | int | None = None
    device_name: str | None = None
    area: str | None = None


class LutronButton(BaseModel):
    device_id: int
    current_state: int | str
    button_number: str | int
    name: str | None = None
    type: str | None = None
    model: str | None = None
    serial: str | int | None = None
    parent_device: str | None = None


### Lifecycle


async def startup() -> None:
    LOGGER.debug("Running Lutron startup hook")
    await BRIDGE.connect()


async def shutdown() -> None:
    LOGGER.debug("Running Lutron shutdown hook")
    await BRIDGE.close()


### Devices


async def get_devices() -> list[LutronDevice]:
    devices = (await asyncio.to_thread(BRIDGE.get_devices)).values()
    return [LutronDevice.model_validate(device) for device in devices]


async def get_device(device_id: str) -> LutronDevice:
    try:
        device = await asyncio.to_thread(BRIDGE.get_device_by_id, device_id)
        return LutronDevice.model_validate(device)
    except KeyError:
        raise HTTPException(404, f"Lutron device {device_id} not found")


### Switches


async def turn_on_device(device_id: str) -> None:
    await BRIDGE.set_value(device_id, 100)


async def turn_off_device(device_id: str) -> None:
    await BRIDGE.set_value(device_id, 0)


### Buttons


async def get_buttons() -> list[LutronButton]:
    buttons = (await asyncio.to_thread(BRIDGE.get_buttons)).values()
    return [LutronButton.model_validate(button) for button in buttons]


async def get_button(device_id: str) -> LutronButton:
    button = next((btn for btn in await get_buttons() if btn.device_id == device_id), None)
    if button is None:
        raise HTTPException(404, f"Button {device_id} not found")
    return button


async def tap_button(button_id: str) -> None:
    try:
        await BRIDGE.tap_button(button_id)
    except KeyError:
        raise HTTPException(404, f"Button {button_id} not found")


### Events


def add_button_listener(*button_ids: str, listener: LutronButtonListener):
    if not len(button_ids):
        button_ids = tuple(btn["device_id"] for btn in BRIDGE.get_buttons().values())
    for button_id in button_ids:
        BRIDGE.add_button_subscriber(button_id, LutronButtonHandler(button_id, listener))
