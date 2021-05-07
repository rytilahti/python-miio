import warnings
from enum import IntEnum
from typing import Optional, Tuple

import click

from .click_common import command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException
from .utils import int_to_rgb, rgb_to_int


class YeelightException(DeviceException):
    pass


class YeelightMode(IntEnum):
    RGB = 1
    ColorTemperature = 2
    HSV = 3


class YeelightStatus(DeviceStatus):
    def __init__(self, data):
        # ['name', 'lan_ctrl', 'save_state', 'delayoff', 'music_on', 'power', 'bright', 'color_mode', 'rgb',      'hue', 'sat', 'ct',   'flowing', 'flow_params', 'active_mode', 'nl_br', 'bg_power', 'bg_bright', 'bg_lmode', 'bg_rgb',   'bg_hue', 'bg_sat', 'bg_ct', 'bg_flowing', 'bg_flow_params']
        # ['name', '1',        '1',          '60',       '1',        'on',    '100',    '2',          '16711680', '359', '100', '3584', '1',       '[0, 24, 0]',  '1',           '100',   'on',       '100',       '2',        '16711680', '359',    '100',    '3584',  '1',          '[0, 24, 0]']
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
        rgb = self.data["rgb"]
        if self.color_mode == YeelightMode.RGB and rgb:
            return int_to_rgb(int(rgb))
        return None

    @property
    def color_mode(self) -> YeelightMode:
        """Return current color mode."""
        return YeelightMode(int(self.data["color_mode"]))

    @property
    def hsv(self) -> Optional[Tuple[int, int, int]]:
        """Return current color in HSV if HSV mode is active."""
        hue = self.data["hue"]
        sat = self.data["sat"]
        brightness = self.data["bright"]
        if self.color_mode == YeelightMode.HSV and (hue or sat or brightness):
            return hue, sat, brightness
        return None

    @property
    def color_temp(self) -> Optional[int]:
        """Return current color temperature, if applicable."""
        ct = self.data["ct"]
        if self.color_mode == YeelightMode.ColorTemperature and ct:
            return int(ct)
        return None

    @property
    def developer_mode(self) -> Optional[bool]:
        """Return whether the developer mode is active."""
        lan_ctrl = self.data["lan_ctrl"]
        if lan_ctrl:
            return bool(int(lan_ctrl))
        return None

    @property
    def save_state_on_change(self) -> bool:
        """Return whether the bulb state is saved on change."""
        return bool(int(self.data["save_state"]))

    @property
    def name(self) -> str:
        """Return the internal name of the bulb."""
        return self.data["name"]

    @property
    def color_flowing(self) -> bool:
        """Return whether the color flowing is active."""
        return bool(int(self.data["flowing"]))

    @property
    def color_flow_params(self) -> Optional[str]:
        """Return color flowing params."""
        if self.color_flowing:
            return self.data["flow_params"]
        return None

    @property
    def delay_off(self) -> int:
        """Return delay in minute before bulb is off."""
        return int(self.data["delayoff"])

    @property
    def music_mode(self) -> Optional[bool]:
        """Return whether the music mode is active."""
        music_on = self.data["music_on"]
        if music_on:
            return bool(int(music_on))
        return None

    @property
    def moonlight_mode(self) -> Optional[bool]:
        """Return whether the moonlight mode is active."""
        active_mode = self.data["active_mode"]
        if active_mode:
            return bool(int(active_mode))
        return None

    @property
    def moonlight_mode_brightness(self) -> Optional[int]:
        """Return current moonlight brightness."""
        nl_br = self.data["nl_br"]
        if nl_br:
            return int(self.data["nl_br"])
        return None

    @property
    def is_bg_on(self) -> Optional[bool]:
        """Return whether the background light is on or off."""
        bg_power = self.data["bg_power"]
        if bg_power:
            return bg_power == "on"
        return None

    @property
    def bg_brightness(self) -> Optional[int]:
        """Return current background lights brightness."""
        if self.is_bg_on is not None:
            return int(self.data["bg_bright"])
        return None

    @property
    def bg_rgb(self) -> Optional[Tuple[int, int, int]]:
        """Return background lights color in RGB if RGB mode is active."""
        rgb = self.data["bg_rgb"]
        if self.bg_color_mode == YeelightMode.RGB and rgb:
            return int_to_rgb(int(rgb))
        return None

    @property
    def bg_color_mode(self) -> Optional[YeelightMode]:
        """Return current background lights color mode."""
        if self.is_bg_on is not None:
            return YeelightMode(int(self.data["bg_lmode"]))
        return None

    @property
    def bg_hsv(self) -> Optional[Tuple[int, int, int]]:
        """Return current background lights color in HSV if HSV mode is active."""
        hue = self.data["bg_hue"]
        sat = self.data["bg_sat"]
        brightness = self.data["bg_bright"]
        if self.bg_color_mode == YeelightMode.HSV and (hue or sat or brightness):
            return hue, sat, brightness
        return None

    @property
    def bg_color_temp(self) -> Optional[int]:
        """Return current background lights color temperature, if applicable."""
        ct = self.data["bg_ct"]
        if self.bg_color_mode == YeelightMode.ColorTemperature and ct:
            return int(ct)
        return None

    @property
    def bg_color_flowing(self) -> Optional[bool]:
        """Return whether the flowing mode is active for background lights."""
        if self.is_bg_on is not None:
            return bool(int(self.data["bg_flowing"]))
        return None

    @property
    def bg_color_flow_params(self) -> Optional[str]:
        """Return color flowing params for background lights."""
        if self.bg_color_flowing:
            return self.data["bg_flow_params"]
        return None


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
        warnings.warn(
            "Please consider using python-yeelight " "for more complete support.",
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

    @command(
        default_output=format_output(
            "",
            "Name: {result.name}\n"
            "Developer mode: {result.developer_mode}\n"
            "Update default on change: {result.save_state_on_change}\n"
            "Delay in minute before off: {result.delay_off}\n"
            "Music mode: {result.music_mode}\n"
            "Light\n"
            "   Power: {result.is_on}\n"
            "   Brightness: {result.brightness}\n"
            "   Color mode: {result.color_mode}\n"
            "   RGB: {result.rgb}\n"
            "   HSV: {result.hsv}\n"
            "   Temperature: {result.color_temp}\n"
            "   Color flowing mode: {result.color_flowing}\n"
            "   Color flowing parameters: {result.color_flow_params}\n"
            "Moonlight\n"
            "   Is in mode: {result.moonlight_mode}\n"
            "   Moonlight mode brightness: {result.moonlight_mode_brightness}\n"
            "Background light\n"
            "   Power: {result.is_bg_on}\n"
            "   Brightness: {result.bg_brightness}\n"
            "   Color mode: {result.bg_color_mode}\n"
            "   RGB: {result.bg_rgb}\n"
            "   HSV: {result.bg_hsv}\n"
            "   Temperature: {result.bg_color_temp}\n"
            "   Color flowing mode: {result.bg_color_flowing}\n"
            "   Color flowing parameters: {result.bg_color_flow_params}\n"
            "\n",
        )
    )
    def status(self) -> YeelightStatus:
        """Retrieve properties."""
        properties = [
            # general properties
            "name",
            "lan_ctrl",
            "save_state",
            "delayoff",
            "music_on",
            # light properties
            "power",
            "bright",
            "color_mode",
            "rgb",
            "hue",
            "sat",
            "ct",
            "flowing",
            "flow_params",
            # moonlight properties
            "active_mode",
            "nl_br",
            # background light properties
            "bg_power",
            "bg_bright",
            "bg_lmode",
            "bg_rgb",
            "bg_hue",
            "bg_sat",
            "bg_ct",
            "bg_flowing",
            "bg_flow_params",
        ]

        values = self.get_properties(properties)

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
        default_output=format_output("Setting brightness to {level}"),
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
        default_output=format_output("Setting color temperature to {level}"),
    )
    def set_color_temp(self, level, transition=500):
        """Set color temp in kelvin."""
        if level > 6500 or level < 1700:
            raise YeelightException("Invalid color temperature: %s" % level)
        if transition > 0:
            return self.send("set_ct_abx", [level, "smooth", transition])
        else:
            # Bedside lamp requires transition
            return self.send("set_ct_abx", [level, "sudden", 0])

    @command(
        click.argument("rgb", default=[255] * 3, type=click.Tuple([int, int, int])),
        default_output=format_output("Setting color to {rgb}"),
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
        default_output=format_output("Setting developer mode to {enable}"),
    )
    def set_developer_mode(self, enable: bool) -> bool:
        """Enable or disable the developer mode."""
        return self.send("set_ps", ["cfg_lan_ctrl", str(int(enable))])

    @command(
        click.argument("enable", type=bool),
        default_output=format_output("Setting save state on change {enable}"),
    )
    def set_save_state_on_change(self, enable: bool) -> bool:
        """Enable or disable saving the state on changes."""
        return self.send("set_ps", ["cfg_save_state", str(int(enable))])

    @command(
        click.argument("name", type=str),
        default_output=format_output("Setting name to {name}"),
    )
    def set_name(self, name: str) -> bool:
        """Set an internal name for the bulb."""
        return self.send("set_name", [name])

    @command(default_output=format_output("Toggling the bulb"))
    def toggle(self):
        """Toggle bulb state."""
        return self.send("toggle")

    @command(default_output=format_output("Setting current settings to default"))
    def set_default(self):
        """Set current state as default."""
        return self.send("set_default")

    def set_scene(self, scene, *vals):
        """Set the scene."""
        raise NotImplementedError("Setting the scene is not implemented yet.")
        # return self.send("set_scene", [scene, *vals])
