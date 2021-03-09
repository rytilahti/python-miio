import enum
import logging
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
_MAPPING = {
    # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:heater:0000A01A:zhimi-mc2:1
    # Heater (siid=2)
    "power": {"siid": 2, "piid": 1},
    "target_temperature": {"siid": 2, "piid": 5},
    # Countdown (siid=3)
    "countdown_time": {"siid": 3, "piid": 1},
    # Environment (siid=4)
    "temperature": {"siid": 4, "piid": 7},
    # Physical Control Locked (siid=6)
    "child_lock": {"siid": 5, "piid": 1},
    # Alarm (siid=6)
    "buzzer": {"siid": 6, "piid": 1},
    # Indicator light (siid=7)
    "led_brightness": {"siid": 7, "piid": 3},
}

HEATER_PROPERTIES = {
    "temperature_range": (18, 28),
    "delay_off_range": (0, 12 * 3600),
}


class LedBrightness(enum.Enum):
    On = 0
    Off = 1


class HeaterMiotException(DeviceException):
    pass


class HeaterMiotStatus(DeviceStatus):
    """Container for status reports from the Xiaomi Smart Space Heater S."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response (MIoT format) of Xiaomi Smart Space Heater S (zhimi.heater.mc2):

        [
          { "did": "power", "siid": 2, "piid": 1, "code": 0, "value": False },
          { "did": "target_temperature", "siid": 2, "piid": 5, "code": 0, "value": 18 },
          { "did": "countdown_time", "siid": 3, "piid": 1, "code": 0, "value": 0 },
          { "did": "temperature", "siid": 4, "piid": 7, "code": 0, "value": 22.6 },
          { "did": "child_lock", "siid": 5, "piid": 1, "code": 0, "value": False },
          { "did": "buzzer", "siid": 6, "piid": 1, "code": 0, "value": False },
          { "did": "led_brightness", "siid": 7, "piid": 3, "code": 0, "value": 0 }
        ]
        """
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.is_on else "off"

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.data["power"]

    @property
    def target_temperature(self) -> int:
        """Target temperature."""
        return self.data["target_temperature"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["countdown_time"]

    @property
    def temperature(self) -> float:
        """Current temperature."""
        return self.data["temperature"]

    @property
    def child_lock(self) -> bool:
        """True if child lock is on, False otherwise."""
        return self.data["child_lock"] is True

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on, False otherwise."""
        return self.data["buzzer"] is True

    @property
    def led_brightness(self) -> LedBrightness:
        """LED indicator brightness."""
        return LedBrightness(self.data["led_brightness"])


class HeaterMiot(MiotDevice):
    """Main class representing the Xiaomi Smart Space Heater S (zhimi.heater.mc2)."""

    mapping = _MAPPING

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Temperature: {result.temperature} °C\n"
            "Target Temperature: {result.target_temperature} °C\n"
            "LED indicator brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Power-off time: {result.delay_off_countdown} hours\n",
        )
    )
    def status(self) -> HeaterMiotStatus:
        """Retrieve properties."""

        return HeaterMiotStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(
        click.argument("target_temperature", type=int),
        default_output=format_output(
            "Setting target temperature to '{target_temperature}'"
        ),
    )
    def set_target_temperature(self, target_temperature: int):
        """Set target_temperature ."""
        min_temp, max_temp = HEATER_PROPERTIES["temperature_range"]
        if target_temperature < min_temp or target_temperature > max_temp:
            raise HeaterMiotException(
                "Invalid temperature: %s. Must be between %s and %s."
                % (target_temperature, min_temp, max_temp)
            )
        return self.set_property("target_temperature", target_temperature)

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.set_property("child_lock", lock)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.set_property("buzzer", buzzer)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output(
            "Setting LED indicator brightness to {brightness}"
        ),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.set_property("led_brightness", brightness.value)

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds"),
    )
    def set_delay_off(self, seconds: int):
        """Set delay off seconds."""
        min_delay, max_delay = HEATER_PROPERTIES["delay_off_range"]
        if seconds < min_delay or seconds > max_delay:
            raise HeaterMiotException(
                "Invalid scheduled turn off: %s. Must be between %s and %s"
                % (seconds, min_delay, max_delay)
            )
        return self.set_property("countdown_time", seconds // 3600)
