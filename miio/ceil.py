import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class CeilException(DeviceException):
    pass


class CeilStatus:
    """Container for status reports from Xiaomi Philips LED Ceiling Lamp."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'power': 'off', 'bright': 0, 'snm': 4, 'dv': 0,
        #  'cctsw': [[0, 3], [0, 2], [0, 1]], 'bl': 1,
        #  'mb': 1, 'ac': 1, 'mssw': 1, 'cct': 99}

        # NOTE: Only 8 properties can be requested at the same time
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
    def scene(self) -> int:
        """Current fixed scene (brightness & colortemp)."""
        return self.data["snm"]

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in seconds."""
        return self.data["dv"]

    @property
    def color_temperature(self) -> int:
        """Current color temperature."""
        return self.data["cct"]

    @property
    def smart_night_light(self) -> bool:
        """Smart night mode state."""
        return self.data["bl"] == 1

    @property
    def automatic_color_temperature(self) -> bool:
        """Automatic color temperature state."""
        return self.data["ac"] == 1

    def __repr__(self) -> str:
        s = "<CeilStatus power=%s, " \
            "brightness=%s, " \
            "color_temperature=%s, " \
            "scene=%s, " \
            "delay_off_countdown=%s, " \
            "smart_night_light=%s, " \
            "automatic_color_temperature=%s>" % \
            (self.power,
             self.brightness,
             self.color_temperature,
             self.scene,
             self.delay_off_countdown,
             self.smart_night_light,
             self.automatic_color_temperature)
        return s

    def __json__(self):
        return self.data


class Ceil(Device):
    """Main class representing Xiaomi Philips LED Ceiling Lamp."""

    # TODO: - Auto On/Off Not Supported
    #       - Adjust Scenes with Wall Switch Not Supported

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Brightness: {result.brightness}\n"
            "Color temperature: {result.color_temperature}\n"
            "Scene: {result.scene}\n"
            "Delayed turn off: {result.delay_off_countdown}\n"
            "Smart night light: {result.smart_night_light}\n"
            "Automatic color temperature: {result.automatic_color_temperature}\n"
        )
    )
    def status(self) -> CeilStatus:
        """Retrieve properties."""
        properties = ['power', 'bright', 'cct', 'snm', 'dv', 'bl', 'ac', ]
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

        return CeilStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering on"),
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
            raise CeilException("Invalid brightness: %s" % level)

        return self.send("set_bright", [level])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting color temperature to {level}")
    )
    def set_color_temperature(self, level: int):
        """Set Correlated Color Temperature."""
        if level < 1 or level > 100:
            raise CeilException("Invalid color temperature: %s" % level)

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
            raise CeilException("Invalid brightness: %s" % brightness)

        if cct < 1 or cct > 100:
            raise CeilException("Invalid color temperature: %s" % cct)

        return self.send("set_bricct", [brightness, cct])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds")
    )
    def delay_off(self, seconds: int):
        """Turn off delay in seconds."""

        if seconds < 1:
            raise CeilException(
                "Invalid value for a delayed turn off: %s" % seconds)

        return self.send("delay_off", [seconds])

    @command(
        click.argument("number", type=int),
        default_output=format_output("Setting fixed scene to {number}")
    )
    def set_scene(self, number: int):
        """Set a fixed scene. 4 fixed scenes are available (1-4)"""
        if number < 1 or number > 4:
            raise CeilException("Invalid fixed scene number: %s" % number)

        return self.send("apply_fixed_scene", [number])

    @command(
        default_output=format_output("Turning on smart night light"),
    )
    def smart_night_light_on(self):
        """Smart Night Light On."""
        return self.send("enable_bl", [1])

    @command(
        default_output=format_output("Turning off smart night light"),
    )
    def smart_night_light_off(self):
        """Smart Night Light off."""
        return self.send("enable_bl", [0])

    @command(
        default_output=format_output("Turning on automatic color temperature"),
    )
    def automatic_color_temperature_on(self):
        """Automatic color temperature on."""
        return self.send("enable_ac", [1])

    @command(
        default_output=format_output("Turning off automatic color temperature"),
    )
    def automatic_color_temperature_off(self):
        """Automatic color temperature off."""
        return self.send("enable_ac", [0])
