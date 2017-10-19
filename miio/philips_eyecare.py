import logging
from .device import Device
from typing import Any, Dict
from collections import defaultdict

_LOGGER = logging.getLogger(__name__)


class PhilipsEyecareStatus:
    """Container for status reports from Xiaomi Philips Eyecare Smart Lamp 2"""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ['power': 'off', 'bright': 5, 'notifystatus': 'off',
        #  'ambstatus': 'off': 'ambvalue': 41, 'eyecare': 'on',
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
        """Current brightness."""
        return self.data["bright"]

    @property
    def reminder(self) -> bool:
        """True if reminder is on. FIXME be more descriptive"""
        return self.data["notifystatus"] == "on"

    @property
    def ambient(self) -> bool:
        """True if ambient is on. FIXME be more descriptive."""
        return self.data["ambstatus"] == "on"

    @property
    def ambient_brightness(self) -> int:
        """Ambient brightness level."""
        return self.data["ambvalue"]

    @property
    def eyecare(self) -> bool:
        """True if eyecare is on."""
        return self.data["eyecare"] == "on"

    @property
    def scene(self) -> int:
        """Current scene."""
        return self.data["scene_num"]

    @property
    def smart_night_light(self) -> bool:
        """True if smart night light is on."""
        return self.data["bls"] == "on"

    @property
    def delay_off_countdown(self) -> int:
        """Current delay off counter."""
        return self.data["dvalue"]

    def __str__(self) -> str:
        s = "<PhilipsEyecareStatus power=%s, brightness=%s, " \
            "notify=%s, ambient=%s, ambient_brightness=%s, " \
            "eyecare=%s, scene=%s, smart_night_light=%s, " \
            "delay_off_countdown=%s>" % \
            (self.power, self.brightness,
             self.reminder, self.ambient, self.ambient_brightness,
             self.eyecare, self.scene, self.smart_night_light,
             self.delay_off_countdown)
        return s


class PhilipsEyecare(Device):
    """Main class representing Xiaomi Philips Eyecare Smart Lamp 2."""

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

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def eyecare_on(self):
        """Eyecare on."""
        return self.send("set_eyecare", ["on"])

    def eyecare_off(self):
        """Eyecare off."""
        return self.send("set_eyecare", ["off"])

    def set_brightness(self, level: int):
        """Set brightness level."""
        return self.send("set_bright", [level])

    def set_scene(self, num: int):
        """Set eyecare user scene."""
        return self.send("set_user_scene", [num])

    def delay_off(self, minutes: int):
        """Set delay off minutes."""
        return self.send("delay_off", [minutes])

    def smart_night_light_on(self):
        """Night Light On."""
        return self.send("enable_bl", ["on"])

    def smart_night_light_off(self):
        """Night Light Off."""
        return self.send("enable_bl", ["off"])

    def reminder_on(self):
        """Eye Fatigue Reminder On."""
        return self.send("set_notifyuser", ["on"])

    def reminder_off(self):
        """Eye Fatigue Reminder Off."""
        return self.send("set_notifyuser", ["off"])

    def ambient_on(self):
        """Amblient Light On."""
        return self.send("enable_amb", ["on"])

    def ambient_off(self):
        """Ambient Light Off."""
        return self.send("enable_amb", ["off"])

    def set_ambient_brightness(self, level: int):
        """Set Ambient Light brightness level."""
        return self.send("set_amb_bright", [level])
