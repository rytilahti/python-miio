from .device import Device
from typing import Tuple, Optional
from enum import IntEnum


class YeelightMode(IntEnum):
    RGB = 1
    ColorTemperature = 2
    HSV = 3


class YeelightStatus:
    def __init__(self, data):
        self.data = data

    @property
    def is_on(self) -> bool:
        return self.data["power"] == "on"

    @property
    def bright(self) -> int:
        return int(self.data["bright"])

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        if self.color_mode == YeelightMode.RGB:
            rgb = self.data["rgb"]
            blue = rgb & 0xff
            green = (rgb >> 8) & 0xff
            red = (rgb >> 16) & 0xff
            return red, green, blue
        return None

    @property
    def color_mode(self) -> YeelightMode:
        return YeelightMode(int(self.data["color_mode"]))

    @property
    def hsv(self) -> Optional[Tuple[int, int, int]]:
        if self.color_mode == YeelightMode.HSV:
            return self.data["hue"], self.data["sat"], self.data["bright"]
        return None

    @property
    def color_temp(self) -> Optional[int]:
        if self.color_mode == YeelightMode.ColorTemperature:
            return int(self.data["ct"])
        return None

    @property
    def name(self) -> str:
        return self.data["name"]

    def __repr__(self):
        s = "<Yeelight on=%s mode=%s bright=%s color_temp=%s " \
            "rgb=%s hsv=%s name=%s>" % \
            (self.is_on,
             self.color_mode,
             self.bright,
             self.color_temp,
             self.rgb,
             self.hsv,
             self.name)
        return s


class Yeelight(Device):
    """A rudimentary support for Yeelight bulbs.

    The API is the same as defined in
    https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf
    and only partially implmented here.

    For a more complete implementation please refer to python-yeelight package
    (https://yeelight.readthedocs.io/en/latest/),
    which however requires enabling the developer mode on the bulbs.
    """

    SUPPORTED = ['yeelink-light-color1', 'yeelink-light-mono1']

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def set_bright(self, bright):
        return self.send("set_bright", [bright])

    def set_color_temp(self, ct):
        return self.send("set_ct_abx", [ct, "smooth", 500])

    def set_rgb(self, rgb):
        return self.send("set_rgb", [rgb])

    def set_hsv(self, hsv):
        return self.send("set_hsv", [hsv])

    def toggle(self):
        """Toggles bulb state."""
        return self.send("toggle")

    def set_default(self):
        """Sets current state as default."""
        return self.send("set_default")

    def set_scene(self, scene, *vals):
        return self.send("set_scene", [scene, *vals])

    def status(self):
        """Retrieve properties."""
        properties = [
            "power",
            "bright",
            "ct",
            "rgb",
            "hue",
            "sat",
            "color_mode",
            "name"
        ]

        values = self.send(
            "get_prop",
            properties
        )

        return YeelightStatus(dict(zip(properties, values)))
