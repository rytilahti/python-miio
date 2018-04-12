import enum
import logging
from typing import Any, Dict, Optional

import click

from .click_common import command, format_output, EnumType
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

class FanException(DeviceException):
    pass


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
        """
        Response of a Fan (zhimi.fan.v3):

        {'temp_dec': 232, 'humidity': 46, 'angle': 30, 'speed': 298,
         'poweroff_time': 0, 'power': 'on', 'ac_power': 'off', 'battery': 98,
         'angle_enable': 'off', 'speed_level': 1, 'natural_level': 0,
         'child_lock': 'off', 'buzzer': 'on', 'led_b': 1, 'led': 'on'}
        """
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
    def natural_speed(self) -> int:
        """Speed level in natural mode."""
        return self.data["natural_level"]

    @property
    def direct_speed(self) -> int:
        """Speed level in direct mode."""
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
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["poweroff_time"]

    @property
    def speed(self) -> int:
        """Speed of the motor."""
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
            "natural_speed=%s, " \
            "direct_speed=%s, " \
            "oscillate=%s, " \
            "battery=%s, " \
            "ac_power=%s, " \
            "delay_off_countdown=%s, " \
            "speed=%s, " \
            "angle=%s" % \
            (self.power,
             self.temperature,
             self.humidity,
             self.led,
             self.led_brightness,
             self.buzzer,
             self.child_lock,
             self.natural_speed,
             self.direct_speed,
             self.oscillate,
             self.battery,
             self.ac_power,
             self.delay_off_countdown,
             self.speed,
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
        default_output=format_output("Setting speed of the natural mode to {speed}")
    )
    def set_natural_speed(self, speed: int):
        """Set natural level."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.send("set_natural_level", [speed])

    @command(
        click.argument("speed", type=int),
        default_output=format_output("Setting speed of the direct mode to {speed}")
    )
    def set_direct_speed(self, speed: int):
        """Set speed of the direct mode."""
        if speed < 0 or speed > 100:
            raise FanException("Invalid speed: %s" % speed)

        return self.send("set_speed_level", [speed])

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
    def set_angle(self, angle: int):
        """Set angle."""
        return self.send("set_angle", [angle])

    @command(
        click.argument("oscillate", type=bool),
        default_output=format_output(
            lambda lock: "Turning on oscillate"
            if lock else "Turning off oscillate"
        )
    )
    def set_oscillate(self, oscillate: bool):
        """Set oscillate on/off."""
        if oscillate:
            return self.send("set_angle_enable", ["on"])
        else:
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
        click.argument("led", type=bool),
        default_output=format_output(
            lambda led: "Turning on LED"
            if led else "Turning off LED"
        )
    )
    def set_led(self, led: bool):
        """Turn led on/off."""
        if led:
            return self.send("set_led", ['on'])
        else:
            return self.send("set_led", ['off'])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer"
            if buzzer else "Turning off buzzer"
        )
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        if buzzer:
            return self.send("set_buzzer", ["on"])
        else:
            return self.send("set_buzzer", ["off"])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock"
            if lock else "Turning off child lock"
        )
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds")
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""

        if seconds < 1:
            raise FanException(
                "Invalid value for a delayed turn off: %s" % seconds)

        return self.send("poweroff_time", [seconds])
