from .device import Device
from typing import Tuple, Optional
from enum import IntEnum
import warnings


class YeelightMode(IntEnum):
    RGB = 1
    ColorTemperature = 2
    HSV = 3


class YeelightStatus:
    def __init__(self, data):
        # ['power', 'bright', 'ct',   'rgb',      'hue', 'sat', 'color_mode', 'name', 'lan_ctrl', 'save_state']
        # ['on',    '100',    '3584', '16711680', '359', '100', '2',          'name', '1',        '1']
        self.data = data

    @property
    def is_on(self) -> bool:
        """Return whether the bulb is on or off."""
        return self.data["power"] == "on"

    @property
    def brightness(self) -> int:
        """Return current brightness."""
        return int(self.data["bright"])

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """Return color in RGB if RGB mode is active."""
        if self.color_mode == YeelightMode.RGB:
            rgb = self.data["rgb"]
            blue = rgb & 0xff
            green = (rgb >> 8) & 0xff
            red = (rgb >> 16) & 0xff
            return red, green, blue
        return None

    @property
    def color_mode(self) -> YeelightMode:
        """Return current color mode."""
        return YeelightMode(int(self.data["color_mode"]))

    @property
    def hsv(self) -> Optional[Tuple[int, int, int]]:
        """Return current color in HSV if HSV mode is active."""
        if self.color_mode == YeelightMode.HSV:
            return self.data["hue"], self.data["sat"], self.data["bright"]
        return None

    @property
    def color_temp(self) -> Optional[int]:
        """Return current color temperature, if applicable."""
        if self.color_mode == YeelightMode.ColorTemperature:
            return int(self.data["ct"])
        return None

    @property
    def developer_mode(self) -> bool:
        """Return whether the developer mode is active."""
        return bool(int(self.data["lan_ctrl"]))

    @property
    def save_state_on_change(self) -> bool:
        """Return whether the bulb state is saved on change."""
        return bool(int(self.data["save_state"]))

    @property
    def name(self) -> str:
        """Return the internal name of the bulb."""
        return self.data["name"]

    def __repr__(self):
        s = "<Yeelight on=%s mode=%s brightness=%s color_temp=%s " \
            "rgb=%s hsv=%s dev=%s save_state=%s name=%s>" % \
            (self.is_on,
             self.color_mode,
             self.brightness,
             self.color_temp,
             self.rgb,
             self.hsv,
             self.developer_mode,
             self.save_state_on_change,
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
    def __init__(self, *args, **kwargs):
        warnings.warn("Please consider using python-yeelight "
                      "for more complete support.", stacklevel=2)
        super().__init__(*args, **kwargs)

    def on(self):
        """Power on."""
        """
        set_power ["on|off", "smooth", time_in_ms, mode]
        where mode:
        0: last mode
        1: normal mode
        2: rgb mode
        3: hsv mode
        4: color flow
        5: moonlight
        """
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def set_brightness(self, bright):
        """Set brightness."""
        return self.send("set_bright", [bright])

    def set_color_temp(self, ct):
        """Set color temp in kelvin."""
        return self.send("set_ct_abx", [ct, "smooth", 500])

    def set_rgb(self, rgb):
        """Set color in encoded RGB."""
        return self.send("set_rgb", [rgb])

    def set_hsv(self, hsv):
        """Set color in HSV."""
        return self.send("set_hsv", [hsv])

    def set_developer_mode(self, enable: bool) -> bool:
        """Enable or disable the developer mode."""
        return self.send("set_ps", ["cfg_lan_ctrl", str(int(enable))])

    def set_save_state_on_change(self, enable: bool) -> bool:
        """Enable or disable saving the state on changes."""
        return self.send("set_ps", ["cfg_save_state"], str(int(enable)))

    def set_name(self, name: str) -> bool:
        """Set an internal name for the bulb."""
        return self.send("set_name", [name])

    def toggle(self):
        """Toggle bulb state."""
        return self.send("toggle")

    def set_default(self):
        """Set current state as default."""
        return self.send("set_default")

    def set_scene(self, scene, *vals):
        """Set the scene."""
        raise NotImplementedError("Setting the scene is not implemented yet.")
        # return self.send("set_scene", [scene, *vals])

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
            "name",
            "lan_ctrl",
            "save_state"
        ]

        values = self.send(
            "get_prop",
            properties
        )

        return YeelightStatus(dict(zip(properties, values)))

    def __str__(self):
        return "<Yeelight at %s: %s>" % (self.ip, self.token)
