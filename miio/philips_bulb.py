import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class PhilipsBulbException(DeviceException):
    pass


class PhilipsBulbStatus:
    """Container for status reports from Xiaomi Philips LED Ceiling Lamp"""

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'power': 'on', 'bright': 85, 'cct': 9, 'snm': 0, 'dv': 0}
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def brightness(self) -> int:
        return self.data["bright"]

    @property
    def color_temperature(self) -> int:
        return self.data["cct"]

    @property
    def scene(self) -> int:
        return self.data["snm"]

    @property
    def delay_off_countdown(self) -> int:
        return self.data["dv"]

    def __repr__(self) -> str:
        s = "<PhilipsBulbStatus power=%s, brightness=%s, " \
            "color_temperature=%s, scene=%s, delay_off_countdown=%s>" % \
            (self.power, self.brightness,
             self.color_temperature, self.scene, self.delay_off_countdown)
        return s

    def __json__(self):
        return self.data


class PhilipsBulb(Device):
    """Main class representing Xiaomi Philips LED Ball Lamp."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Brightness: {result.brightness}\n"
            "Color temperature: {result.color_temperature}\n"
            "Scene: {result.scene}\n"
            "Delayed turn off: {result.delay_off_countdown}\n"
        )
    )
    def status(self) -> PhilipsBulbStatus:
        """Retrieve properties."""
        properties = ['power', 'bright', 'cct', 'snm', 'dv', ]
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

        return PhilipsBulbStatus(
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
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}")
    )
    def set_brightness(self, level: int):
        """Set brightness level."""
        if level < 1 or level > 100:
            raise PhilipsBulbException("Invalid brightness: %s" % level)

        return self.send("set_bright", [level])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting color temperature to {level}")
    )
    def set_color_temperature(self, level: int):
        """Set Correlated Color Temperature."""
        if level < 1 or level > 100:
            raise PhilipsBulbException("Invalid color temperature: %s" % level)

        return self.send("set_cct", [level])

    @command(
        click.argument("brightness", type=int),
        click.argument("cct", type=int),
        default_output=format_output(
            "Setting brightness to {brightness} and color temperature to {cct}")
    )
    def set_brightness_and_color_temperature(self, brightness: int, cct: int):
        """Set brightness level and the correlated color temperature."""
        if brightness < 1 or brightness > 100:
            raise PhilipsBulbException("Invalid brightness: %s" % brightness)

        if cct < 1 or cct > 100:
            raise PhilipsBulbException("Invalid color temperature: %s" % cct)

        return self.send("set_bricct", [brightness, cct])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds")
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""

        if seconds < 1:
            raise PhilipsBulbException(
                "Invalid value for a delayed turn off: %s" % seconds)

        return self.send("delay_off", [seconds])

    @command(
        click.argument("number", type=int),
        default_output=format_output("Setting fixed scene to {number}")
    )
    def set_scene(self, number: int):
        """Set scene number."""
        if number < 1 or number > 4:
            raise PhilipsBulbException("Invalid fixed scene number: %s" % number)

        return self.send("apply_fixed_scene", [number])
