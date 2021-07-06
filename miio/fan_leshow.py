import enum
import logging
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_FAN_LESHOW_SS4 = "leshow.fan.ss4"

AVAILABLE_PROPERTIES_COMMON = [
    "power",
    "mode",
    "blow",
    "timer",
    "sound",
    "yaw",
    "fault",
]

AVAILABLE_PROPERTIES = {
    MODEL_FAN_LESHOW_SS4: AVAILABLE_PROPERTIES_COMMON,
}


class FanLeshowException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Manual = 0
    Sleep = 1
    Strong = 2
    Natural = 3


class FanLeshowStatus(DeviceStatus):
    """Container for status reports from the Xiaomi Rosou SS4 Ventilator."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Leshow Fan SS4 (leshow.fan.ss4):

        {'power': 1, 'mode': 2, 'blow': 100, 'timer': 0,
         'sound': 1, 'yaw': 0, 'fault': 0}
        """
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] == 1 else "off"

    @property
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.data["power"] == 1

    @property
    def mode(self) -> OperationMode:
        """Operation mode."""
        return OperationMode(self.data["mode"])

    @property
    def speed(self) -> int:
        """Speed of the fan in percent."""
        return self.data["blow"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["sound"] == 1

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["yaw"] == 1

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in minutes."""
        return self.data["timer"]

    @property
    def error_detected(self) -> bool:
        """True if a fault was detected."""
        return self.data["fault"] == 1


class FanLeshow(Device):
    """Main class representing the Xiaomi Rosou SS4 Ventilator."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_FAN_LESHOW_SS4,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_FAN_LESHOW_SS4

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Speed: {result.speed}\n"
            "Buzzer: {result.buzzer}\n"
            "Oscillate: {result.oscillate}\n"
            "Power-off time: {result.delay_off_countdown}\n"
            "Error detected: {result.error_detected}\n",
        )
    )
    def status(self) -> FanLeshowStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES[self.model]
        values = self.get_properties(properties, max_properties=15)

        return FanLeshowStatus(dict(zip(properties, values)))

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
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode (manual, natural, sleep, strong)."""
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed of the manual mode to {speed}"),
    )
    def set_speed(self, speed: int):
        """Set a speed level between 0 and 100."""
        if speed < 0 or speed > 100:
            raise FanLeshowException("Invalid speed: %s" % speed)

        return self.send("set_blow", [speed])

    @command(
        click.argument("oscillate", type=bool),
        default_output=format_output(
            lambda oscillate: "Turning on oscillate"
            if oscillate
            else "Turning off oscillate"
        ),
    )
    def set_oscillate(self, oscillate: bool):
        """Set oscillate on/off."""
        return self.send("set_yaw", [int(oscillate)])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.send("set_sound", [int(buzzer)])

    @command(
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes"),
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0 or minutes > 540:
            raise FanLeshowException(
                "Invalid value for a delayed turn off: %s" % minutes
            )

        return self.send("set_timer", [minutes])
