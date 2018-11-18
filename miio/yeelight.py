import warnings
import click
from enum import IntEnum
from typing import Tuple, Optional

from .click_common import command, format_output
from .device import Device, DeviceException
from .utils import int_to_rgb, rgb_to_int


class YeelightException(DeviceException):
    pass


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
            return int_to_rgb(int(self.data["rgb"]))
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

    @command(
        default_output=format_output(
            "",
            "Name: {result.name}\n"
            "Power: {result.is_on}\n"
            "Brightness: {result.brightness}\n"
            "Color mode: {result.color_mode}\n"
            "RGB: {result.rgb}\n"
            "HSV: {result.hsv}\n"
            "Temperature: {result.color_temp}\n"
            "Developer mode: {result.developer_mode}\n"
            "Update default on change: {result.save_state_on_change}\n"
            "\n")
    )
    def status(self) -> YeelightStatus:
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

    @command(
        click.option("--transition", type=int, required=False, default=0),
        click.option("--mode", type=int, required=False, default=0),
        default_output=format_output("Powering on"),
    )
    def on(self, transition=0, mode=0):
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
        if transition > 0 or mode > 0:
            return self.send("set_power", ["on", "smooth", transition, mode])
        return self.send("set_power", ["on"])

    @command(
        click.option("--transition", type=int, required=False, default=0),
        default_output=format_output("Powering off"),
    )
    def off(self, transition=0):
        """Power off."""
        if transition > 0:
            return self.send("set_power", ["off", "smooth", transition])
        return self.send("set_power", ["off"])

    @command(
        click.argument("level", type=int),
        click.option("--transition", type=int, required=False, default=0),
        default_output=format_output("Setting brightness to {level}")
    )
    def set_brightness(self, level, transition=0):
        """Set brightness."""
        if level < 0 or level > 100:
            raise YeelightException("Invalid brightness: %s" % level)
        if transition > 0:
            return self.send("set_bright", [level, "smooth", transition])
        return self.send("set_bright", [level])

    @command(
        click.argument("level", type=int),
        click.option("--transition", type=int, required=False, default=0),
        default_output=format_output("Setting color temperature to {level}")
    )
    def set_color_temp(self, level, transition=500):
        """Set color temp in kelvin."""
        if level > 6500 or level < 1700:
            raise YeelightException("Invalid color temperature: %s" % level)
        if transition > 0:
            return self.send("set_ct_abx", [level, "smooth", transition])
        else:
            return self.send("set_ct_abx", [level])

    @command(
        click.argument("rgb", default=[255] * 3, type=click.Tuple([int, int, int])),
        default_output=format_output("Setting color to {rgb}")
    )
    def set_rgb(self, rgb: Tuple[int, int, int]):
        """Set color in RGB."""
        for color in rgb:
            if color < 0 or color > 255:
                raise YeelightException("Invalid color: %s" % color)

        return self.send("set_rgb", [rgb_to_int(rgb)])

    def set_hsv(self, hsv):
        """Set color in HSV."""
        return self.send("set_hsv", [hsv])

    @command(
        click.argument("enable", type=bool),
        default_output=format_output("Setting developer mode to {enable}")
    )
    def set_developer_mode(self, enable: bool) -> bool:
        """Enable or disable the developer mode."""
        return self.send("set_ps", ["cfg_lan_ctrl", str(int(enable))])

    @command(
        click.argument("enable", type=bool),
        default_output=format_output("Setting save state on change {enable}")
    )
    def set_save_state_on_change(self, enable: bool) -> bool:
        """Enable or disable saving the state on changes."""
        return self.send("set_ps", ["cfg_save_state", str(int(enable))])

    @command(
        click.argument("name", type=bool),
        default_output=format_output("Setting name to {enable}")
    )
    def set_name(self, name: str) -> bool:
        """Set an internal name for the bulb."""
        return self.send("set_name", [name])

    @command(
        default_output=format_output("Toggling the bulb"),
    )
    def toggle(self):
        """Toggle bulb state."""
        return self.send("toggle")

    @command(
        default_output=format_output("Setting current settings to default"),
    )
    def set_default(self):
        """Set current state as default."""
        return self.send("set_default")

    def set_scene(self, scene, *vals):
        """Set the scene."""
        raise NotImplementedError("Setting the scene is not implemented yet.")
        # return self.send("set_scene", [scene, *vals])

    def __str__(self):
        return "<Yeelight at %s: %s>" % (self.ip, self.token)
