import enum
import logging
from typing import Any

import click

from miio import Device, DeviceStatus
from miio.click_common import EnumType, command, format_output
from miio.devicestatus import sensor, setting

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


class OperationMode(enum.Enum):
    Manual = 0
    Sleep = 1
    Strong = 2
    Natural = 3


class FanLeshowStatus(DeviceStatus):
    """Container for status reports from the Xiaomi Rosou SS4 Ventilator."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Response of a Leshow Fan SS4 (leshow.fan.ss4):

        {'power': 1, 'mode': 2, 'blow': 100, 'timer': 0,
         'sound': 1, 'yaw': 0, 'fault': 0}
        """
        self.data = data

    @property
    @sensor("Power", icon="mdi:power")
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] == 1 else "off"

    @property
    @sensor("Is On", icon="mdi:power")
    def is_on(self) -> bool:
        """True if device is turned on."""
        return self.data["power"] == 1

    @property
    @setting(
        "Mode",
        setter_name="set_mode",
        icon="mdi:fan",
        choices=OperationMode,
    )
    def mode(self) -> OperationMode:
        """Operation mode."""
        return OperationMode(self.data["mode"])

    @property
    @setting(
        "Speed",
        setter_name="set_speed",
        icon="mdi:speedometer",
        unit="%",
        min_value=0,
        max_value=100,
        step=1,
    )
    def speed(self) -> int:
        """Speed of the fan in percent."""
        return self.data["blow"]

    @property
    @setting("Buzzer", setter_name="set_buzzer", icon="mdi:volume-high")
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["sound"] == 1

    @property
    @setting("Oscillate", setter_name="set_oscillate", icon="mdi:rotate-3d-variant")
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["yaw"] == 1

    @property
    @setting(
        "Delay Off Countdown",
        setter_name="delay_off",
        icon="mdi:timer",
        device_class="duration",
        unit="min",
        min_value=0,
        max_value=540,
        step=1,
    )
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in minutes."""
        return self.data["timer"]

    @property
    @sensor("Error Detected", icon="mdi:alert-circle")
    def error_detected(self) -> bool:
        """True if a fault was detected."""
        return self.data["fault"] == 1


class FanLeshow(Device):
    """Main class representing the Xiaomi Rosou SS4 Ventilator."""

    _supported_models = list(AVAILABLE_PROPERTIES.keys())

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
        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_FAN_LESHOW_SS4]
        )
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
            raise ValueError("Invalid speed: %s" % speed)

        return self.send("set_blow", [speed])

    @command(
        click.argument("oscillate", type=bool),
        default_output=format_output(
            lambda oscillate: (
                "Turning on oscillate" if oscillate else "Turning off oscillate"
            )
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
            raise ValueError("Invalid value for a delayed turn off: %s" % minutes)

        return self.send("set_timer", [minutes])
