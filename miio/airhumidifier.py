import enum
import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from .click_common import command, format_output, EnumType
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class AirHumidifierException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Silent = 'silent'
    Medium = 'medium'
    High = 'high'
    Auto = 'auto'


class LedBrightness(enum.Enum):
    Bright = 0
    Dim = 1
    Off = 2


class AirHumidifierStatus:
    """Container for status reports from the air humidifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Humidifier (zhimi.humidifier.v1):

        {'power': 'off', 'mode': 'high', 'temp_dec': 294,
         'humidity': 33, 'buzzer': 'on', 'led_b': 0,
         'child_lock': 'on', 'limit_hum': 40, 'trans_level': 85,
         'speed': None, 'depth': None, 'dry': None, 'use_time': 941100,
         'hw_version': 0, 'button_pressed': 'led'}
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
        """Operation mode. Can be either silent, medium or high."""
        return OperationMode(self.data["mode"])

    @property
    def temperature(self) -> Optional[float]:
        """Current temperature, if available."""
        if self.data["temp_dec"] is not None:
            return self.data["temp_dec"] / 10.0
        return None

    @property
    def humidity(self) -> int:
        """Current humidity."""
        return self.data["humidity"]

    @property
    def buzzer(self) -> bool:
        """True if buzzer is turned on."""
        return self.data["buzzer"] == "on"

    @property
    def led_brightness(self) -> Optional[LedBrightness]:
        """LED brightness if available."""
        if self.data["led_b"] is not None:
            return LedBrightness(self.data["led_b"])
        return None

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"] == "on"

    @property
    def target_humidity(self) -> int:
        """Target humiditiy. Can be either 30, 40, 50, 60, 70, 80 percent."""
        return self.data["limit_hum"]

    @property
    def trans_level(self) -> int:
        """The meaning of the property is unknown."""
        return self.data["trans_level"]

    @property
    def speed(self) -> Optional[int]:
        """Current fan speed."""
        return self.data["speed"]

    @property
    def depth(self) -> Optional[int]:
        """Current depth."""
        return self.data["depth"]

    @property
    def dry(self) -> Optional[bool]:
        """Return True if dry mode is on if available."""
        if self.data["dry"] is not None:
            return self.data["dry"] == "on"
        return None

    @property
    def use_time(self) -> Optional[int]:
        """How long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def hardware_version(self) -> Optional[str]:
        """The hardware version."""
        return self.data["hw_version"]

    @property
    def button_pressed(self) -> Optional[str]:
        """Last pressed button."""
        return self.data["button_pressed"]

    def __repr__(self) -> str:
        s = "<AirHumidiferStatus power=%s, " \
            "mode=%s, " \
            "temperature=%s, " \
            "humidity=%s%%, " \
            "led_brightness=%s, " \
            "buzzer=%s, " \
            "child_lock=%s, " \
            "target_humidity=%s%%, " \
            "trans_level=%s, " \
            "speed=%s, " \
            "depth=%s, " \
            "dry=%s, " \
            "use_time=%s, " \
            "hardware_version=%s, " \
            "button_pressed=%s>" % \
            (self.power,
             self.mode,
             self.temperature,
             self.humidity,
             self.led_brightness,
             self.buzzer,
             self.child_lock,
             self.target_humidity,
             self.trans_level,
             self.speed,
             self.depth,
             self.dry,
             self.use_time,
             self.hardware_version,
             self.button_pressed)
        return s

    def __json__(self):
        return self.data


class AirHumidifier(Device):
    """Implementation of Xiaomi Mi Air Humidifier."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "Temperature: {result.temperature} °C\n"
            "Humidity: {result.humidity} %\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Target humidity: {result.target_humidity} %\n"
            "Trans level: {result.trans_level}\n"
            "Speed: {result.speed}\n"
            "Depth: {result.depth}\n"
            "Dry: {result.dry}\n"
            "Use time: {result.use_time}\n"
            "Hardware version: {result.hardware_version}\n"
            "Button pressed: {result.button_pressed}\n"
        )
    )
    def status(self) -> AirHumidifierStatus:
        """Retrieve properties."""

        properties = ['power', 'mode', 'temp_dec', 'humidity', 'buzzer',
                      'led_b', 'child_lock', 'limit_hum', 'trans_level',
                      'speed', 'depth', 'dry', 'use_time', 'button_pressed',
                      'hw_version', ]

        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return AirHumidifierStatus(
            defaultdict(lambda: None, zip(properties, values)))

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
        click.argument("mode", type=EnumType(OperationMode, False)),
        default_output=format_output("Setting mode to '{mode.value}'")
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("brightness", type=EnumType(LedBrightness, False)),
        default_output=format_output(
            "Setting LED brightness to {brightness}")
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.send("set_led_b", [brightness.value])

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
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity to {humidity}")
    )
    def set_target_humidity(self, humidity: int):
        """Set the target humidity."""
        if humidity not in [30, 40, 50, 60, 70, 80]:
            raise AirHumidifierException(
                "Invalid target humidity: %s" % humidity)

        return self.send("set_limit_hum", [humidity])

    @command(
        click.argument("dry", type=bool),
        default_output=format_output(
            lambda dry: "Turning on dry mode"
            if dry else "Turning off dry mode"
        )
    )
    def set_dry(self, dry: bool):
        """Set dry mode on/off."""
        if dry:
            return self.send("set_dry", ["on"])
        else:
            return self.send("set_dry", ["off"])
