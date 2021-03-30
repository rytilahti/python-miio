import enum
import logging
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


class OperationSensitivity(enum.Enum):
    High = 1
    Medium = 2
    Low = 3


class WalkingpadStatus(DeviceStatus):
    """Container for status reports from Xiaomi Walkingpad.

    Input data dictionary to initialise this class:

    {'cal': '0',
     'dist': '0',
     'mode': 2,
     'power': 'off',
     'sensitivity': 1,
     'sp': '0.0',
     'start_speed': 3.0,
     'step': '0',
     'time': '0'}
    """

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
    def start_speed(self) -> float:
        """Current speed."""
        return self.data["start_speed"]

    @property
    def mode(self) -> OperationMode:
        """Current mode."""
        return self.data["mode"]

    @property
    def sensitivity(self) -> OperationSensitivity:
        """Current sensitivity."""
        return self.data["sensitivity"]

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
        """Current calories burnt."""
        return self.data["cal"]


class Walkingpad(Device):
    """Main class representing Xiaomi Walkingpad."""

    @command(
        default_output=format_output(
            "",
            "Mode: {result.mode}\n"
            "Time: {result.time}\n"
            "Steps: {result.step_count}\n"
            "Speed: {result.speed}\n"
            "Start Speed: {result.start_speed}\n"
            "Sensitivity: {result.sensitivity}\n"
            "Distance: {result.distance}\n"
            "Calories: {result.calories}",
        )
    )
    def status(self) -> WalkingpadStatus:
        """Retrieve properties."""

        properties = ["all"]

        # Walkingpad A1 only allows 1 property to be read at a time
        values = self.get_properties(properties, max_properties=1)

        data = {}
        for x in values:
            prop, value = x.split(":")
            data[prop] = value

        properties_additional = ["power", "mode", "start_speed", "sensitivity"]
        values_additional = self.get_properties(properties_additional, max_properties=1)

        additional_props = dict(zip(properties_additional, values_additional))
        data.update(additional_props)

        return WalkingpadStatus(data)

    @command(
        default_output=format_output(
            "",
            "Mode: {result.mode}\n"
            "Time: {result.time}\n"
            "Steps: {result.step_count}\n"
            "Speed: {result.speed}\n"
            "Distance: {result.distance}\n"
            "Calories: {result.calories}",
        )
    )
    def quick_status(self) -> WalkingpadStatus:
        """Retrieve quick properties."""

        # Walkingpad A1 allows you to retrieve a subset of values with "all"
        # eg ['mode:1', 'time:1387', 'sp:3.0', 'dist:1150', 'cal:71710', 'step:2117']

        properties = ["all"]

        # Walkingpad A1 only allows 1 property to be read at a time
        values = self.get_properties(properties, max_properties=1)
        # print(values)
        data = {}
        for x in values:
            prop, value = x.split(":")
            data[prop] = value

        return WalkingpadStatus(data)

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(default_output=format_output("Locking"))
    def lock(self):
        """Lock device."""
        return self.send("set_lock", [1])

    @command(default_output=format_output("Unlocking"))
    def unlock(self):
        """Unlock device."""
        return self.send("set_lock", [0])

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

    @command(
        click.argument("speed", type=float),
        default_output=format_output("Setting start speed to {speed}"),
    )
    def set_start_speed(self, speed: float):
        """Set start speed."""

        if not isinstance(speed, float):
            raise WalkingpadException("Invalid start speed: %s" % speed)

        if speed < 0 or speed > 6:
            raise WalkingpadException("Invalid start speed: %s" % speed)

        return self.send("set_start_speed", [speed])

    @command(
        click.argument("sensitivity", type=EnumType(OperationSensitivity)),
        default_output=format_output("Setting sensitivity to {sensitivity}"),
    )
    def set_sensitivity(self, sensitivity: OperationSensitivity):
        """Set sensitivity."""

        if not isinstance(sensitivity, OperationSensitivity):
            raise WalkingpadException("Invalid mode: %s" % sensitivity)

        return self.send("set_sensitivity", [sensitivity.value])
