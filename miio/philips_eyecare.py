import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class PhilipsEyecareException(DeviceException):
    pass


class PhilipsEyecareStatus:
    """Container for status reports from Xiaomi Philips Eyecare Smart Lamp 2"""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ['power': 'off', 'bright': 5, 'notifystatus': 'off',
        #  'ambstatus': 'off', 'ambvalue': 41, 'eyecare': 'on',
        #  'scene_num': 3, 'bls': 'on', 'dvalue': 0]
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
        """Current brightness of the primary light."""
        return self.data["bright"]

    @property
    def reminder(self) -> bool:
        """Indicates the eye fatigue notification is enabled or not."""
        return self.data["notifystatus"] == "on"

    @property
    def ambient(self) -> bool:
        """True if the ambient light (second light source) is on."""
        return self.data["ambstatus"] == "on"

    @property
    def ambient_brightness(self) -> int:
        """Brightness of the ambient light."""
        return self.data["ambvalue"]

    @property
    def eyecare(self) -> bool:
        """True if the eyecare mode is on."""
        return self.data["eyecare"] == "on"

    @property
    def scene(self) -> int:
        """Current fixed scene."""
        return self.data["scene_num"]

    @property
    def smart_night_light(self) -> bool:
        """True if the smart night light mode is on."""
        return self.data["bls"] == "on"

    @property
    def delay_off_countdown(self) -> int:
        """Countdown until turning off in minutes."""
        return self.data["dvalue"]

    def __repr__(self) -> str:
        s = "<PhilipsEyecareStatus power=%s, " \
            "brightness=%s, " \
            "ambient=%s, " \
            "ambient_brightness=%s, " \
            "eyecare=%s, " \
            "scene=%s, " \
            "reminder=%s, " \
            "smart_night_light=%s, " \
            "delay_off_countdown=%s>" % \
            (self.power,
             self.brightness,
             self.ambient,
             self.ambient_brightness,
             self.eyecare,
             self.scene,
             self.reminder,
             self.smart_night_light,
             self.delay_off_countdown)
        return s

    def __json__(self):
        return self.data


class PhilipsEyecare(Device):
    """Main class representing Xiaomi Philips Eyecare Smart Lamp 2."""

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Brightness: {result.brightness}\n"
            "Ambient light: {result.ambient}\n"
            "Ambient light brightness: {result.ambient_brightness}\n"
            "Eyecare mode: {result.eyecare}\n"
            "Scene: {result.scence}\n"
            "Eye fatigue reminder: {result.reminder}\n"
            "Smart night light: {result.smart_night_light}\n"
            "Delayed turn off: {result.delay_off_countdown}\n"
        )
    )
    def status(self) -> PhilipsEyecareStatus:
        """Retrieve properties."""
        properties = ['power', 'bright', 'notifystatus', 'ambstatus',
                      'ambvalue', 'eyecare', 'scene_num', 'bls',
                      'dvalue', ]
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

        return PhilipsEyecareStatus(
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
        default_output=format_output("Turning on eyecare mode"),
    )
    def eyecare_on(self):
        """Turn the eyecare mode on."""
        return self.send("set_eyecare", ["on"])

    @command(
        default_output=format_output("Turning off eyecare mode"),
    )
    def eyecare_off(self):
        """Turn the eyecare mode off."""
        return self.send("set_eyecare", ["off"])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}")
    )
    def set_brightness(self, level: int):
        """Set brightness level of the primary light."""
        if level < 1 or level > 100:
            raise PhilipsEyecareException("Invalid brightness: %s" % level)

        return self.send("set_bright", [level])

    @command(
        click.argument("number", type=int),
        default_output=format_output("Setting fixed scene to {number}")
    )
    def set_scene(self, number: int):
        """Set one of the fixed eyecare user scenes."""
        if number < 1 or number > 4:
            raise PhilipsEyecareException("Invalid fixed scene number: %s" % number)

        return self.send("set_user_scene", [number])

    @command(
        click.argument("minutes", type=int),
        default_output=format_output("Setting delayed turn off to {minutes} minutes")
    )
    def delay_off(self, minutes: int):
        """Set delay off minutes."""

        if minutes < 0:
            raise PhilipsEyecareException(
                "Invalid value for a delayed turn off: %s" % minutes)

        return self.send("delay_off", [minutes])

    @command(
        default_output=format_output("Turning on smart night light"),
    )
    def smart_night_light_on(self):
        """Turn the smart night light mode on."""
        return self.send("enable_bl", ["on"])

    @command(
        default_output=format_output("Turning off smart night light"),
    )
    def smart_night_light_off(self):
        """Turn the smart night light mode off."""
        return self.send("enable_bl", ["off"])

    @command(
        default_output=format_output("Turning on eye fatigue reminder"),
    )
    def reminder_on(self):
        """Enable the eye fatigue reminder / notification."""
        return self.send("set_notifyuser", ["on"])

    @command(
        default_output=format_output("Turning off eye fatigue reminder"),
    )
    def reminder_off(self):
        """Disable the eye fatigue reminder / notification."""
        return self.send("set_notifyuser", ["off"])

    @command(
        default_output=format_output("Turning on ambient light"),
    )
    def ambient_on(self):
        """Turn the ambient light on."""
        return self.send("enable_amb", ["on"])

    @command(
        default_output=format_output("Turning off ambient light"),
    )
    def ambient_off(self):
        """Turn the ambient light off."""
        return self.send("enable_amb", ["off"])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}")
    )
    def set_ambient_brightness(self, level: int):
        """Set the brightness of the ambient light."""
        if level < 1 or level > 100:
            raise PhilipsEyecareException(
                "Invalid ambient brightness: %s" % level)

        return self.send("set_amb_bright", [level])
