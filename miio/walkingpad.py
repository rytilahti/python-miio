import enum
import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


class WalkingpadException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Auto = 0
    Manual = 1
    Off = 2


class WalkingpadStatus(DeviceStatus):
    """Container for status reports from Xiaomi Walkingpad."""

    # raw_command set_start_speed '["1.0"]' finally made my WalkingPad autostart on speed 1! Hurray!
    #
    # raw_command get_prop '["mode"]' returns
    #
    # [0] while mode is auto
    #     [1] while mode is manual
    #     [2] when in standby
    # raw_command get_prop '["step"]' returns [2303]
    # raw_command get_prop '["time"]' returns [1970] (while time is 32:50)
    # raw_command get_prop '["dist"]' returns [1869]
    # raw_command get_prop '["cal"]' returns [67340]
    # raw_command get_prop '["goal"]' returns [0, 60]
    # raw_command get_prop '["max"]' returns [6.0]
    # raw_command get_prop '["initial"]' returns [3]
    # raw_command get_prop '["offline"]' returns [0]
    # raw_command get_prop '["sensitivity"]' returns [2]
    # raw_command get_prop '["sp"]' returns [1.0]
    # raw_command get_prop '["start_speed"]' returns [1.0]
    # raw_command get_prop '["auto"]' returns [1]
    # raw_command get_prop '["disp"]' returns [19]
    # raw_command get_prop '["lock"]' returns [0]

    def __init__(self, data: Dict[str, Any]) -> None:

        # NOTE: Only 1 property can be requested at the same time
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == "on"

    @property
    def time(self) -> int:
        """Current walking time."""
        return self.data["time"]

    @property
    def speed(self) -> float:
        """Current speed."""
        return self.data["sp"]

    @property
    def mode(self) -> int:
        """Current mode."""
        return self.data["mode"]

    @property
    def step_count(self) -> int:
        """Current steps."""
        return self.data["step"]

    @property
    def distance(self) -> int:
        """Current distance."""
        return self.data["dist"]

    @property
    def calories(self) -> int:
        """Current distance."""
        return self.data["cal"]


class Walkingpad(Device):
    """Main class representing Xiaomi Walkingpad."""

    # TODO: - Auto On/Off Not Supported
    #       - Adjust Scenes with Wall Switch Not Supported

    @command(
        default_output=format_output(
            "",
            "Mode: {result.mode}\n"
            "Time: {result.time}\n"
            "Steps: {result.step}\n"
            "Speed: {result.speed}\n"
            "Distance: {result.distance}\n"
            "Calories: {result.calories}  ",
        )
    )
    def status(self) -> WalkingpadStatus:
        """Retrieve properties."""

        # Walkingpad A1 allows you to retrieve a subset of values with "all"
        # eg ['mode:1', 'time:1387', 'sp:3.0', 'dist:1150', 'cal:71710', 'step:2117']

        properties = ["all"]

        # Walkingpad A1 only allows 1 property to be read at a time

        values = self.get_properties(properties, max_properties=1)

        # When running the tests, for some reason the list provided is passed within another list, so I take
        # care of this here.

        if any(isinstance(el, list) for el in values):
            values = values[0]

        data = {}
        for x in values:
            prop, value = x.split(":")
            data[prop] = value

        properties_additional = ["power", "mode"]
        values_additional = self.get_properties(properties_additional, max_properties=1)

        for i in range(len(properties_additional)):
            data[properties_additional[i]] = values_additional[i]

        return WalkingpadStatus(defaultdict(lambda: None, data))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(default_output=format_output("Starting the treadmill"))
    def start(self):
        """Starting Up."""
        return self.send("set_state", ["run"])

    @command(default_output=format_output("Stopping the treadmill"))
    def stop(self):
        """Starting Up."""
        return self.send("set_state", ["stop"])

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.name}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode (auto/manual)."""

        if not isinstance(mode, OperationMode):
            raise WalkingpadException("Invalid mode: %s" % mode)

        return self.send("set_mode", [mode.value])

    @command(
        click.argument("speed", type=float),
        default_output=format_output("Setting speed to {speed}"),
    )
    def set_speed(self, speed: float):
        """Set speed."""

        if not isinstance(speed, float):
            raise WalkingpadException("Invalid speed: %s" % speed)

        if speed < 0 or speed > 6:
            raise WalkingpadException("Invalid speed: %s" % speed)

        return self.send("set_speed", [speed])
