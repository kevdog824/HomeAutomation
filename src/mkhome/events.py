import logging
import time
import typing as _t

from filelock import FileLock

from mkhome.bridges import bond, lutron
from mkhome.utils.async_utils import run_sync


type _Coro[T] = _t.Coroutine[_t.Any, _t.Any, T]


LOGGER = logging.getLogger(__name__)
OFFICE_LIGHT_LOCK = FileLock(".locks/office-lights.lock")
OFFICE_FAN_LOCK = FileLock(".locks/office-fan.lock")
MASTER_BEDROOM_LIGHT_LOCK = FileLock(".locks/master-bedroom-lights.lock")
MASTER_BEDROOM_FAN_LOCK = FileLock(".locks/master-bedroom-fan.lock")


### Lifecycle


async def startup() -> None:
    LOGGER.debug("Running events startup hook")
    lutron.add_button_listener(listener=noop)
    lutron.add_button_listener("126", listener=office_light_on)
    lutron.add_button_listener("127", listener=office_light_dim_mode)
    lutron.add_button_listener("128", listener=office_light_off)
    lutron.add_button_listener("129", listener=office_fan_speed_up)
    lutron.add_button_listener("130", listener=office_fan_speed_down)
    lutron.add_button_listener("131", listener=master_bedroom_light_on)
    lutron.add_button_listener("132", listener=master_bedroom_light_dim_mode)
    lutron.add_button_listener("133", listener=master_bedroom_light_off)
    lutron.add_button_listener("134", listener=master_bedroom_fan_speed_up)
    lutron.add_button_listener("135", listener=master_bedroom_fan_speed_down)


async def shutdown() -> None:
    LOGGER.debug("Running events shutdown hook")


### Event Utilities


def get_device_by_name(device_name: str) -> bond.BondDevice:
    device_ids = run_sync(bond.get_devices())
    for device_id in device_ids:
        device = run_sync(bond.get_device(device_id))
        if device.name == device_name:
            LOGGER.debug("Device information: %s", device.model_dump_json(indent=4))
            return device
    raise RuntimeError(f"Bond device '{device_name}' not found")


def get_office_ceiling_fan() -> bond.BondDevice:
    return get_device_by_name("Office Ceiling Fan")


def get_master_bedroom_ceiling_fan() -> bond.BondDevice:
    return get_device_by_name("Master Bedroom Ceiling Fan")


### Misc Events


def noop(*_: _t.Any) -> None: ...


### Office Lights


def office_light_on(button_id: str, action: lutron.ButtonAction) -> None:
    with OFFICE_LIGHT_LOCK:
        device = get_office_ceiling_fan()
        LOGGER.info("Button %s: Turning on office light", button_id)
        match action:
            case "SINGLE_CLICK":
                run_sync(bond.light_on(device.device_id))
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Toggling office light", button_id)
                run_sync(bond.set_light_belief_state(device.device_id, 0))
                time.sleep(1)
                run_sync(bond.light_on(device.device_id))
            case "LONG_PRESS":
                run_sync(bond.light_on(device.device_id))
        time.sleep(2)


def office_light_off(button_id: str, action: lutron.ButtonAction) -> None:
    with OFFICE_LIGHT_LOCK:
        device = get_office_ceiling_fan()
        LOGGER.info("Button %s: Turning off office light", button_id)
        match action:
            case "SINGLE_CLICK":
                run_sync(bond.light_off(device.device_id))
            case "DOUBLE_CLICK":
                run_sync(bond.set_light_belief_state(device.device_id, 1))
                time.sleep(1)
                run_sync(bond.light_off(device.device_id))
            case "LONG_PRESS":
                run_sync(bond.light_off(device.device_id))
        time.sleep(2)


def office_light_dim_mode(button_id: str, action: lutron.ButtonAction) -> None:
    if action == "SINGLE_CLICK":
        device = get_office_ceiling_fan()
        LOGGER.info("Button %s: Toggling dim mode on office light", button_id)
        run_sync(bond.dim_mode(device.device_id))


### Office Fan


def office_fan_on(button_id: str, action: lutron.ButtonAction) -> None:
    with OFFICE_FAN_LOCK:
        if action == "SINGLE_CLICK":
            device = get_office_ceiling_fan()
            LOGGER.info("Button %s: Turning on office fan", button_id)
            run_sync(bond.set_speed(device.device_id, 3))
            time.sleep(2)


def office_fan_off(button_id: str, action: lutron.ButtonAction) -> None:
    with OFFICE_FAN_LOCK:
        if action == "SINGLE_CLICK":
            device = get_office_ceiling_fan()
            LOGGER.info("Button %s: Turning off office fan", button_id)
            run_sync(bond.set_speed(device.device_id, 0))
            time.sleep(2)


def office_fan_speed_up(button_id: str, action: lutron.ButtonAction) -> None:
    with OFFICE_FAN_LOCK:
        device = get_office_ceiling_fan()
        match action:
            case "SINGLE_CLICK":
                LOGGER.info("Button %s: Increasing speed on office fan", button_id)
                run_sync(bond.increase_speed(device.device_id, 1))
                time.sleep(2)
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Maxing out speed on office fan", button_id)
                props = run_sync(bond.get_properties(device.device_id))
                run_sync(bond.increase_speed(device.device_id, props.max_speed))
                time.sleep(2)


def office_fan_speed_down(button_id: str, action: lutron.ButtonAction) -> None:
    with OFFICE_FAN_LOCK:
        device = get_office_ceiling_fan()
        props = run_sync(bond.get_properties(device.device_id))
        match action:
            case "SINGLE_CLICK":
                LOGGER.info("Button %s: Decreasing speed on office fan", button_id)
                run_sync(bond.decrease_speed(device.device_id, 1))
                time.sleep(2)
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Zeroing out speed on office fan", button_id)
                run_sync(bond.decrease_speed(device.device_id, props.max_speed))
                time.sleep(2)


### Master Bedroom Lights


def master_bedroom_light_on(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_LIGHT_LOCK:
        device = get_master_bedroom_ceiling_fan()
        LOGGER.info("Button %s: Turning on master bedroom light", button_id)
        match action:
            case "SINGLE_CLICK":
                run_sync(bond.light_on(device.device_id))
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Toggling master bedroom light", button_id)
                run_sync(bond.set_light_belief_state(device.device_id, 0))
                time.sleep(1)
                run_sync(bond.light_on(device.device_id))
            case "LONG_PRESS":
                run_sync(bond.light_on(device.device_id))
        time.sleep(2)


def master_bedroom_light_off(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_LIGHT_LOCK:
        device = get_master_bedroom_ceiling_fan()
        LOGGER.info("Button %s: Turning off master bedroom light", button_id)
        match action:
            case "SINGLE_CLICK":
                run_sync(bond.light_off(device.device_id))
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Toggling master bedroom light", button_id)
                run_sync(bond.set_light_belief_state(device.device_id, 1))
                time.sleep(1)
                run_sync(bond.light_off(device.device_id))
            case "LONG_PRESS":
                run_sync(bond.light_off(device.device_id))
        time.sleep(2)


def master_bedroom_light_dim_mode(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_LIGHT_LOCK:
        if action == "SINGLE_CLICK":
            device = get_master_bedroom_ceiling_fan()
            LOGGER.info("Button %s: Toggling dim mode on master bedroom light", button_id)
            run_sync(bond.dim_mode(device.device_id))
            time.sleep(2)


### Master Bedroom Fan


def master_bedroom_fan_on(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_FAN_LOCK:
        if action == "SINGLE_CLICK":
            device = get_master_bedroom_ceiling_fan()
            LOGGER.info("Button %s: Turning on master bedroom fan", button_id)
            run_sync(bond.set_speed(device.device_id, 3))
            time.sleep(2)


def master_bedroom_fan_off(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_FAN_LOCK:
        if action == "SINGLE_CLICK":
            device = get_master_bedroom_ceiling_fan()
            LOGGER.info("Button %s: Turning off master bedroom fan", button_id)
            run_sync(bond.set_speed(device.device_id, 0))
            time.sleep(2)


def master_bedroom_fan_speed_up(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_FAN_LOCK:
        device = get_master_bedroom_ceiling_fan()
        match action:
            case "SINGLE_CLICK":
                LOGGER.info("Button %s: Increasing speed on master bedroom fan", button_id)
                run_sync(bond.increase_speed(device.device_id, 1))
                time.sleep(2)
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Maxing out speed on master bedroom fan", button_id)
                props = run_sync(bond.get_properties(device.device_id))
                run_sync(bond.increase_speed(device.device_id, props.max_speed))
                time.sleep(2)


def master_bedroom_fan_speed_down(button_id: str, action: lutron.ButtonAction) -> None:
    with MASTER_BEDROOM_FAN_LOCK:
        device = get_master_bedroom_ceiling_fan()
        match action:
            case "SINGLE_CLICK":
                LOGGER.info("Button %s: Decreasing speed on master bedroom fan", button_id)
                run_sync(bond.decrease_speed(device.device_id, 1))
                time.sleep(2)
            case "DOUBLE_CLICK":
                LOGGER.info("Button %s: Zeroing out speed on master bedroom fan", button_id)
                props = run_sync(bond.get_properties(device.device_id))
                run_sync(bond.decrease_speed(device.device_id, props.max_speed))
                time.sleep(2)
