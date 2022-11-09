import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from miio import Device, DeviceStatus
from miio.click_common import EnumType, command, format_output

_LOGGER = logging.getLogger(__name__)

MODEL_AIRDOG_X3 = "airdog.airpurifier.x3"
MODEL_AIRDOG_X5 = "airdog.airpurifier.x5"
MODEL_AIRDOG_X7SM = "airdog.airpurifier.x7sm"

MODEL_AIRDOG_COMMON = ["power", "mode", "speed", "lock", "clean", "pm"]

AVAILABLE_PROPERTIES = {
    MODEL_AIRDOG_X3: MODEL_AIRDOG_COMMON,
    MODEL_AIRDOG_X5: MODEL_AIRDOG_COMMON,
    MODEL_AIRDOG_X7SM: MODEL_AIRDOG_COMMON + ["hcho"],
}


class OperationMode(enum.Enum):
    Auto = "auto"
    Manual = "manual"
    Idle = "sleep"


class OperationModeMapping(enum.Enum):
    Auto = 0
    Manual = 1
    Idle = 2


class AirDogStatus(DeviceStatus):
    """Container for status reports from the air dog x3."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Air Dog X3 (airdog.airpurifier.x3):

        {'power: 'on', 'mode': 'sleep', 'speed': 1, 'lock': 'unlock',
         'clean': 'n', 'pm': 11, 'hcho': 0}
        """

        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.power == "on"

    @property
    def mode(self) -> OperationMode:
        """Operation mode.

        Can be either auto, manual, sleep.
        """
        return OperationMode(self.data["mode"])

    @property
    def speed(self) -> int:
        """Current speed level."""
        return self.data["speed"]

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["lock"] == "lock"

    @property
    def clean_filters(self) -> bool:
        """True if the display shows "-C-" and the filter must be cleaned."""
        return self.data["clean"] == "y"

    @property
    def pm25(self) -> int:
        """Return particulate matter value (0...300μg/m³)."""
        return self.data["pm"]

    @property
    def hcho(self) -> Optional[int]:
        """Return formaldehyde value."""
        if self.data["hcho"] is not None:
            return self.data["hcho"]

        return None


class AirDogX3(Device):
    """Support for Airdog air purifiers (airdog.airpurifier.x*)."""

    _supported_models = list(AVAILABLE_PROPERTIES.keys())

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Speed: {result.speed}\n"
            "Child lock: {result.child_lock}\n"
            "Clean filters: {result.clean_filters}\n"
            "PM2.5: {result.pm25}\n"
            "Formaldehyde: {result.hcho}\n",
        )
    )
    def status(self) -> AirDogStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_AIRDOG_X3]
        )
        values = self.get_properties(properties, max_properties=10)

        return AirDogStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", [1])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", [0])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        click.argument("speed", type=int, required=False, default=1),
        default_output=format_output(
            "Setting mode to '{mode.value}' and speed to {speed}"
        ),
    )
    def set_mode_and_speed(self, mode: OperationMode, speed: int = 1):
        """Set mode and speed."""
        if mode.value not in (om.value for om in OperationMode):
            raise ValueError(f"{mode.value} is not a valid OperationMode value")

        if mode in [OperationMode.Auto, OperationMode.Idle]:
            speed = 1

        if self.model == MODEL_AIRDOG_X3:
            max_speed = 4
        else:
            # airdog.airpurifier.x7, airdog.airpurifier.x7sm
            max_speed = 5

        if speed < 1 or speed > max_speed:
            raise ValueError("Invalid speed: %s" % speed)

        return self.send("set_wind", [OperationModeMapping[mode.name].value, speed])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.send("set_lock", [int(lock)])

    @command(default_output=format_output("Setting filters cleaned"))
    def set_filters_cleaned(self):
        """Set filters cleaned."""
        return self.send("set_clean")
