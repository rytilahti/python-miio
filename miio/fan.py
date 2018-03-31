import enum
import logging
from typing import Any, Dict, Optional

import click

from .click_common import command, format_output, EnumType
from .device import Device

_LOGGER = logging.getLogger(__name__)


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class MoveDirection(enum.Enum):
    Left = 'left'
    Right = 'right'


class FanStatus:
    """Container for status reports from the Xiaomi Smart Fan."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ['temp_dec', 'humidity', 'angle', 'speed', 'poweroff_time', 'power',
        # 'ac_power', 'battery', 'angle_enable', 'speed_level',
        # 'natural_level', 'child_lock', 'buzzer', 'led_b', 'led']
        #
        # [232, 46, 30, 298, 0, 'on', 'off', 98, 'off', 1, 0, 'off', 'on',
        # 1, 'on']
        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """True if device is currently on."""
        return self.power == "on"

    @property
    def humidity(self) -> int:
        """Current humidity."""
        return self.data["humidity"]

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def led(self) -> bool:
        """True if LED is turned on."""
        return self.data["led"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """LED brightness, if available."""
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] == "on"

    @property
    def child_lock(self) -> bool:
        """True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def natural_level(self) -> int:
        """Fan speed in natural mode."""
        return self.data["natural_level"]

    @property
    def speed_level(self) -> int:
        """Fan speed in direct mode."""
        return self.data["speed_level"]

    @property
    def oscillate(self) -> bool:
        """True if oscillation is enabled."""
        return self.data["angle_enable"] == "on"

    @property
    def battery(self) -> int:
        """Current battery level."""
        return self.data["battery"]

    @property
    def ac_power(self) -> bool:
        """True if powered by AC."""
        return self.data["ac_power"] == "on"

    @property
    def poweroff_time(self) -> int:
        """Time until turning off. FIXME verify"""
        return self.data["poweroff_time"]

    @property
    def speed(self) -> int:
        """FIXME What is the meaning of this value?
        (cp. speed_level vs. natural_level)"""
        return self.data["speed"]

    @property
    def angle(self) -> int:
        """Current angle."""
        return self.data["angle"]

    def __str__(self) -> str:
        s = "<FanStatus power=%s, " \
            "temperature=%s, " \
            "humidity=%s, " \
            "led=%s, " \
            "led_brightness=%s, " \
            "buzzer=%s, " \
            "child_lock=%s, " \
            "natural_level=%s, " \
            "speed_level=%s, " \
            "oscillate=%s, " \
            "battery=%s, " \
            "ac_power=%s, " \
            "poweroff_time=%s, " \
            "speed=%s, " \
            "angle=%s" % \
            (self.power,
             self.temperature,
             self.humidity,
             self.led,
             self.led_brightness,
             self.buzzer,
             self.child_lock,
             self.natural_level,
             self.speed_level,
             self.oscillate,
             self.battery,
             self.ac_power,
             self.poweroff_time,
             self.speed_level,
             self.angle)
        return s

    def __json__(self):
        return self.data


class Fan(Device):
    """Main class representing the Xiaomi Smart Fan."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Battery: {result.battery} %\n"
            "AC power: {result.ac_power}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "LED: {result.led}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Natural level: {result.natural_level}\n"
            "Speed level: {result.speed_level}\n"
            "Oscillate: {result.oscillate}\n"
            "Power-off time: {result.poweroff_time}\n"
            "Speed: {result.speed}\n"
            "Angle: {result.angle}\n"
        )
    )
    def status(self) -> FanStatus:
        """Retrieve properties."""
        properties = ['temp_dec', 'humidity', 'angle', 'speed',
                      'poweroff_time', 'power', 'ac_power', 'battery',
                      'angle_enable', 'speed_level', 'natural_level',
                      'child_lock', 'buzzer', 'led_b', 'led']

        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.error(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return FanStatus(dict(zip(properties, values)))

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering off"),
    )
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting natural level to {level}")
    )
    def set_natural_level(self, level: int):
        """Set natural level."""
        level = max(0, min(level, 100))
        return self.send("set_natural_level", [level])  # 0...100

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed level to {level}")
    )
    def set_speed_level(self, level: int):
        """Set speed level."""
        level = max(0, min(level, 100))
        return self.send("set_speed_level", [level])  # 0...100

    @command(
        click.argument("direction", type=EnumType(MoveDirection, False)),
        default_output=format_output(
            "Setting move direction to {direction}")
    )
    def set_direction(self, direction: MoveDirection):
        """Set move direction."""
        return self.send("set_move", [direction.value])

    @command(
        click.argument("angle", type=int),
        default_output=format_output("Setting angle to {angle}")
    )
    def fan_set_angle(self, angle: int):
        """Set angle."""
        return self.send("set_angle", [angle])

    @command(
        default_output=format_output("Turning on oscillate"),
    )
    def oscillate_on(self):
        """Enable oscillate."""
        return self.send("set_angle_enable", ["on"])

    @command(
        default_output=format_output("Turning off oscillate"),
    )
    def oscillate_off(self):
        """Disable oscillate."""
        return self.send("set_angle_enable", ["off"])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness, False)),
        default_output=format_output(
            "Setting LED brightness to {brightness}")
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_b", [brightness.value])

    @command(
        default_output=format_output("Turning on LED"),
    )
    def led_on(self):
        """Turn led on."""
        return self.send("set_led", ["on"])

    @command(
        default_output=format_output("Turning off LED"),
    )
    def led_off(self):
        """Turn led off."""
        return self.send("set_led", ["off"])

    @command(
        default_output=format_output("Turning on buzzer"),
    )
    def buzzer_on(self):
        """Enable buzzer."""
        return self.send("set_buzzer", ["on"])

    @command(
        default_output=format_output("Turning off buzzer"),
    )
    def buzzer_off(self):
        """Disable buzzer."""
        return self.send("set_buzzer", ["off"])
