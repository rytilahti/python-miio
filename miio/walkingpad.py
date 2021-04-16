import enum
import logging
from datetime import timedelta
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
    """Container for status reports from Xiaomi Walkingpad A1 (ksmb.walkingpad.v3).

    Input data dictionary to initialise this class:

    {'cal': 6130,
     'dist': 90,
     'mode': 1,
     'power': 'on',
     'sensitivity': 1,
     'sp': 3.0,
     'start_speed': 3.0,
     'step': 180,
     'time': 121}
    """

    def __init__(self, data: Dict[str, Any]) -> None:
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
    def walking_time(self) -> timedelta:
        """Current walking duration in seconds."""
        return timedelta(seconds=int(self.data["time"]))

    @property
    def speed(self) -> float:
        """Current speed."""
        return float(self.data["sp"])

    @property
    def start_speed(self) -> float:
        """Current start speed."""
        return self.data["start_speed"]

    @property
    def mode(self) -> OperationMode:
        """Current mode."""
        return OperationMode(self.data["mode"])

    @property
    def sensitivity(self) -> OperationSensitivity:
        """Current sensitivity."""
        return OperationSensitivity(self.data["sensitivity"])

    @property
    def step_count(self) -> int:
        """Current steps."""
        return int(self.data["step"])

    @property
    def distance(self) -> int:
        """Current distance in meters."""
        return int(self.data["dist"])

    @property
    def calories(self) -> int:
        """Current calories burnt."""
        return int(self.data["cal"])


class Walkingpad(Device):
    """Main class representing Xiaomi Walkingpad."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode.name}\n"
            "Time: {result.walking_time}\n"
            "Steps: {result.step_count}\n"
            "Speed: {result.speed}\n"
            "Start Speed: {result.start_speed}\n"
            "Sensitivity: {result.sensitivity.name}\n"
            "Distance: {result.distance}\n"
            "Calories: {result.calories}",
        )
    )
    def status(self) -> WalkingpadStatus:
        """Retrieve properties."""

        data = self._get_quick_status()

        # The quick status only retrieves a subset of the properties. The rest of them are retrieved here.
        properties_additional = ["power", "mode", "start_speed", "sensitivity"]
        values_additional = self.get_properties(properties_additional, max_properties=1)

        additional_props = dict(zip(properties_additional, values_additional))
        data.update(additional_props)

        return WalkingpadStatus(data)

    @command(
        default_output=format_output(
            "",
            "Mode: {result.mode.name}\n"
            "Walking time: {result.walking_time}\n"
            "Steps: {result.step_count}\n"
            "Speed: {result.speed}\n"
            "Distance: {result.distance}\n"
            "Calories: {result.calories}",
        )
    )
    def quick_status(self) -> WalkingpadStatus:
        """Retrieve quick status.

        The walkingpad provides the option to retrieve a subset of properties in one call:
        steps, mode, speed, distance, calories and time.

        `status()` will do four more separate I/O requests for power, mode, start_speed, and sensitivity.
        If you don't need any of that, prefer this method for status updates.
        """

        data = self._get_quick_status()

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
        """Start the treadmill."""

        # In case the treadmill is not already turned on, turn it on.
        if not self.status().is_on:
            self.on()

        return self.send("set_state", ["run"])

    @command(default_output=format_output("Stopping the treadmill"))
    def stop(self):
        """Stop the treadmill."""
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

        # In case the treadmill is not already turned on, throw an exception.
        if not self.status().is_on:
            raise WalkingpadException("Cannot set the speed, device is turned off")

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

        # In case the treadmill is not already turned on, throw an exception.
        if not self.status().is_on:
            raise WalkingpadException(
                "Cannot set the start speed, device is turned off"
            )

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

    def _get_quick_status(self):
        """Internal helper to get the quick status via the "all" property."""

        # Walkingpad A1 allows you to quickly retrieve a subset of values with "all"
        # all other properties need to be retrieved one by one and are therefore slower
        # eg ['mode:1', 'time:1387', 'sp:3.0', 'dist:1150', 'cal:71710', 'step:2117']

        properties = ["all"]

        values = self.get_properties(properties, max_properties=1)

        value_map = {
            "sp": float,
            "step": int,
            "cal": int,
            "time": int,
            "dist": int,
            "mode": int,
        }

        data = {}
        for x in values:
            prop, value = x.split(":")

            if prop not in value_map:
                _LOGGER.warning("Received unknown data from device: %s=%s", prop, value)

            data[prop] = value

        converted_data = {key: value_map[key](value) for key, value in data.items()}

        return converted_data
