import enum
import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_PHILIPS_LIGHT_RWREAD = "philips.light.rwread"

AVAILABLE_PROPERTIES = {
    MODEL_PHILIPS_LIGHT_RWREAD: ["power", "bright", "dv", "snm", "flm", "chl", "flmv"]
}


class PhilipsRwreadException(DeviceException):
    pass


class MotionDetectionSensitivity(enum.Enum):
    Low = 1
    Medium = 2
    High = 3


class PhilipsRwreadStatus(DeviceStatus):
    """Container for status reports from Xiaomi Philips RW Read."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a RW Read (philips.light.rwread):

        {'power': 'on', 'bright': 53, 'dv': 0, 'snm': 1,
         'flm': 0, 'chl': 0, 'flmv': 0}
        """
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
    def brightness(self) -> int:
        """Current brightness."""
        return self.data["bright"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["dv"]

    @property
    def scene(self) -> int:
        """Current fixed scene."""
        return self.data["snm"]

    @property
    def motion_detection(self) -> bool:
        """True if motion detection is enabled."""
        return self.data["flm"] == 1

    @property
    def motion_detection_sensitivity(self) -> MotionDetectionSensitivity:
        """The sensitivity of the motion detection."""
        return MotionDetectionSensitivity(self.data["flmv"])

    @property
    def child_lock(self) -> bool:
        """True if child lock is enabled."""
        return self.data["chl"] == 1


class PhilipsRwread(Device):
    """Main class representing Xiaomi Philips RW Read."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_PHILIPS_LIGHT_RWREAD,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_PHILIPS_LIGHT_RWREAD

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Brightness: {result.brightness}\n"
            "Delayed turn off: {result.delay_off_countdown}\n"
            "Scene: {result.scene}\n"
            "Motion detection: {result.motion_detection}\n"
            "Motion detection sensitivity: {result.motion_detection_sensitivity}\n"
            "Child lock: {result.child_lock}\n",
        )
    )
    def status(self) -> PhilipsRwreadStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties)

        return PhilipsRwreadStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}"),
    )
    def set_brightness(self, level: int):
        """Set brightness level of the primary light."""
        if level < 1 or level > 100:
            raise PhilipsRwreadException("Invalid brightness: %s" % level)

        return self.send("set_bright", [level])

    @command(
        click.argument("number", type=int),
        default_output=format_output("Setting fixed scene to {number}"),
    )
    def set_scene(self, number: int):
        """Set one of the fixed eyecare user scenes."""
        if number < 1 or number > 4:
            raise PhilipsRwreadException("Invalid fixed scene number: %s" % number)

        return self.send("apply_fixed_scene", [number])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds"),
    )
    def delay_off(self, seconds: int):
        """Set delay off in seconds."""

        if seconds < 0:
            raise PhilipsRwreadException(
                "Invalid value for a delayed turn off: %s" % seconds
            )

        return self.send("delay_off", [seconds])

    @command(
        click.argument("motion_detection", type=bool),
        default_output=format_output(
            lambda motion_detection: "Turning on motion detection"
            if motion_detection
            else "Turning off motion detection"
        ),
    )
    def set_motion_detection(self, motion_detection: bool):
        """Set motion detection on/off."""
        return self.send("enable_flm", [int(motion_detection)])

    @command(
        click.argument("sensitivity", type=EnumType(MotionDetectionSensitivity)),
        default_output=format_output(
            "Setting motion detection sensitivity to {sensitivity}"
        ),
    )
    def set_motion_detection_sensitivity(self, sensitivity: MotionDetectionSensitivity):
        """Set motion detection sensitivity."""
        return self.send("set_flmvalue", [sensitivity.value])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.send("enable_chl", [int(lock)])
