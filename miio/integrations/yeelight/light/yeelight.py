import logging
from enum import IntEnum
from typing import List, Optional, Tuple

import click

from miio.click_common import command, format_output
from miio.descriptors import ValidSettingRange
from miio.device import Device, DeviceStatus
from miio.devicestatus import action, sensor, setting
from miio.identifiers import LightId
from miio.utils import int_to_rgb, rgb_to_int

from .spec_helper import YeelightSpecHelper, YeelightSubLightType

_LOGGER = logging.getLogger(__name__)

SUBLIGHT_PROP_PREFIX = {
    YeelightSubLightType.Main: "",
    YeelightSubLightType.Background: "bg_",
}

SUBLIGHT_COLOR_MODE_PROP = {
    YeelightSubLightType.Main: "color_mode",
    YeelightSubLightType.Background: "bg_lmode",
}


class YeelightMode(IntEnum):
    RGB = 1
    ColorTemperature = 2
    HSV = 3


class YeelightSubLight(DeviceStatus):
    def __init__(self, data, type):
        self.data = data
        self.type = type

    def get_prop_name(self, prop) -> str:
        if prop == "color_mode":
            return SUBLIGHT_COLOR_MODE_PROP[self.type]
        else:
            return SUBLIGHT_PROP_PREFIX[self.type] + prop

    @property
    def is_on(self) -> bool:
        """Return whether the light is on or off."""
        return self.data[self.get_prop_name("power")] == "on"

    @property
    def brightness(self) -> int:
        """Return current brightness."""
        return int(self.data[self.get_prop_name("bright")])

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """Return color in RGB if RGB mode is active."""
        rgb_int = self.rgb_int
        if rgb_int is not None:
            return int_to_rgb(rgb_int)

        return None

    @property
    def rgb_int(self) -> Optional[int]:
        """Return color as single integer RGB if RGB mode is active."""
        rgb = self.data[self.get_prop_name("rgb")]
        if self.color_mode == YeelightMode.RGB and rgb:
            return int(rgb)
        return None

    @property
    def color_mode(self) -> Optional[YeelightMode]:
        """Return current color mode."""
        try:
            return YeelightMode(int(self.data[self.get_prop_name("color_mode")]))
        except ValueError:  # white only bulbs
            return None

    @property
    def hsv(self) -> Optional[Tuple[int, int, int]]:
        """Return current color in HSV if HSV mode is active."""
        hue = self.data[self.get_prop_name("hue")]
        sat = self.data[self.get_prop_name("sat")]
        brightness = self.data[self.get_prop_name("bright")]
        if self.color_mode == YeelightMode.HSV and (hue or sat or brightness):
            return hue, sat, brightness
        return None

    @property
    def color_temp(self) -> Optional[int]:
        """Return current color temperature, if applicable."""
        ct = self.data[self.get_prop_name("ct")]
        if self.color_mode == YeelightMode.ColorTemperature and ct:
            return int(ct)
        return None

    @property
    def color_flowing(self) -> bool:
        """Return whether the color flowing is active."""
        return bool(int(self.data[self.get_prop_name("flowing")]))

    @property
    def color_flow_params(self) -> Optional[str]:
        """Return color flowing params."""
        if self.color_flowing:
            return self.data[self.get_prop_name("flow_params")]
        return None


class YeelightStatus(DeviceStatus):
    def __init__(self, data):
        # yeelink.light.ceiling4, yeelink.light.ceiling20
        # {'name': '', 'lan_ctrl': '1', 'save_state': '1', 'delayoff': '0', 'music_on': '',  'power': 'off', 'bright': '1',   'color_mode': '2', 'rgb': '',        'hue': '',    'sat': '',   'ct': '4115', 'flowing': '0', 'flow_params': '0,0,2000,3,0,33,2000,3,0,100',                                                                                                          'active_mode': '1', 'nl_br': '1', 'bg_power': 'off', 'bg_bright': '100', 'bg_lmode': '1', 'bg_rgb': '15531811', 'bg_hue': '65',  'bg_sat': '86', 'bg_ct': '4000', 'bg_flowing': '0', 'bg_flow_params': '0,0,3000,4,16711680,100,3000,4,65280,100,3000,4,255,100'}
        # yeelink.light.ceiling1
        # {'name': '', 'lan_ctrl': '1', 'save_state': '1', 'delayoff': '0', 'music_on': '',  'power': 'off', 'bright': '100', 'color_mode': '2', 'rgb': '',        'hue': '',    'sat': '',   'ct': '5200', 'flowing': '0', 'flow_params': '',                                                                                                                                      'active_mode': '0', 'nl_br': '0', 'bg_power': '',    'bg_bright': '',    'bg_lmode': '',  'bg_rgb': '', 'bg_hue': '', 'bg_sat': '', 'bg_ct': '', 'bg_flowing': '', 'bg_flow_params': ''}
        # yeelink.light.ceiling22 - like yeelink.light.ceiling1 but without "lan_ctrl"
        # {'name': '', 'lan_ctrl': '',  'save_state': '1', 'delayoff': '0', 'music_on': '',  'power': 'off', 'bright': '84',  'color_mode': '2', 'rgb': '',        'hue': '',    'sat': '',   'ct': '4000', 'flowing': '0', 'flow_params': '0,0,800,2,2700,50,800,2,2700,30,1200,2,2700,80,800,2,2700,60,1200,2,2700,90,2400,2,2700,50,1200,2,2700,80,800,2,2700,60,400,2,2700,70', 'active_mode': '0', 'nl_br': '0', 'bg_power': '',    'bg_bright': '',    'bg_lmode': '',  'bg_rgb': '', 'bg_hue': '', 'bg_sat': '', 'bg_ct': '', 'bg_flowing': '', 'bg_flow_params': ''}
        # yeelink.light.color3, yeelink.light.color4, yeelink.light.color5, yeelink.light.strip2
        # {'name': '', 'lan_ctrl': '1', 'save_state': '1', 'delayoff': '0', 'music_on': '0', 'power': 'off', 'bright': '100', 'color_mode': '1', 'rgb': '2353663', 'hue': '186', 'sat': '86', 'ct': '6500', 'flowing': '0', 'flow_params': '0,0,1000,1,16711680,100,1000,1,65280,100,1000,1,255,100',                                                                               'active_mode': '',  'nl_br': '',  'bg_power': '',    'bg_bright': '',    'bg_lmode': '',  'bg_rgb': '', 'bg_hue': '', 'bg_sat': '', 'bg_ct': '', 'bg_flowing': '', 'bg_flow_params': ''}
        self.data = data

    @property
    @setting("Power", setter_name="set_power", id=LightId.On)
    def is_on(self) -> bool:
        """Return whether the light is on or off."""
        return self.lights[0].is_on

    @property
    @setting(
        "Brightness",
        unit="%",
        setter_name="set_brightness",
        max_value=100,
        id=LightId.Brightness,
    )
    def brightness(self) -> int:
        """Return current brightness."""
        return self.lights[0].brightness

    @property
    def rgb(self) -> Optional[Tuple[int, int, int]]:
        """Return color in RGB if RGB mode is active."""
        return self.lights[0].rgb

    @property
    @setting("Color", id=LightId.Color, setter_name="set_rgb_int")
    def rgb_int(self) -> Optional[int]:
        """Return color as single integer if RGB mode is active."""
        return self.lights[0].rgb_int

    @property
    @sensor("Color mode")
    def color_mode(self) -> Optional[YeelightMode]:
        """Return current color mode."""
        return self.lights[0].color_mode

    @property
    @sensor(
        "HSV", setter_name="set_hsv"
    )  # TODO: we need to extend @setting to support tuples to fix this
    def hsv(self) -> Optional[Tuple[int, int, int]]:
        """Return current color in HSV if HSV mode is active."""
        return self.lights[0].hsv

    @property
    @setting(
        "Color temperature",
        id=LightId.ColorTemperature,
        setter_name="set_color_temperature",
        range_attribute="color_temperature_range",
        unit="K",
    )
    def color_temp(self) -> Optional[int]:
        """Return current color temperature, if applicable."""
        return self.lights[0].color_temp

    @property
    @sensor("Color flow active")
    def color_flowing(self) -> bool:
        """Return whether the color flowing is active."""
        return self.lights[0].color_flowing

    @property
    @sensor("Color flow parameters")
    def color_flow_params(self) -> Optional[str]:
        """Return color flowing params."""
        return self.lights[0].color_flow_params

    @property
    @setting("Developer mode enabled", setter_name="set_developer_mode")
    def developer_mode(self) -> Optional[bool]:
        """Return whether the developer mode is active."""
        lan_ctrl = self.data["lan_ctrl"]
        if lan_ctrl:
            return bool(int(lan_ctrl))
        return None

    @property
    @setting("Save state on change enabled", setter_name="set_save_state_on_change")
    def save_state_on_change(self) -> bool:
        """Return whether the bulb state is saved on change."""
        return bool(int(self.data["save_state"]))

    @property
    @sensor("Device name")
    def name(self) -> str:
        """Return the internal name of the bulb."""
        return self.data["name"]

    @property
    @sensor("Delayed turn off in", unit="mins")
    def delay_off(self) -> int:
        """Return delay in minute before bulb is off."""
        return int(self.data["delayoff"])

    @property
    @sensor("Music mode enabled")
    def music_mode(self) -> Optional[bool]:
        """Return whether the music mode is active."""
        music_on = self.data["music_on"]
        if music_on:
            return bool(int(music_on))
        return None

    @property
    @sensor("Moon light mode active")
    def moonlight_mode(self) -> Optional[bool]:
        """Return whether the moonlight mode is active."""
        active_mode = self.data["active_mode"]
        if active_mode:
            return bool(int(active_mode))
        return None

    @property
    @sensor("Moon light mode brightness", unit="%")
    def moonlight_mode_brightness(self) -> Optional[int]:
        """Return current moonlight brightness."""
        nl_br = self.data["nl_br"]
        if nl_br:
            return int(self.data["nl_br"])
        return None

    @property
    def lights(self) -> List[YeelightSubLight]:
        """Return list of sub lights."""
        sub_lights = list({YeelightSubLight(self.data, YeelightSubLightType.Main)})
        bg_power = self.data[
            "bg_power"
        ]  # to do: change this to model spec in the future.
        if bg_power:
            sub_lights.append(
                YeelightSubLight(self.data, YeelightSubLightType.Background)
            )
        return sub_lights


class Yeelight(Device):
    """A rudimentary support for Yeelight bulbs.

    The API is the same as defined in
    https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf
    and only partially implmented here.

    For a more complete implementation please refer to python-yeelight package
    (https://yeelight.readthedocs.io/en/latest/),
    which however requires enabling the developer mode on the bulbs.
    """

    _spec_helper = YeelightSpecHelper()
    _supported_models: List[str] = _spec_helper.supported_models

    def __init__(
        self,
        ip: Optional[str] = None,
        token: Optional[str] = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: Optional[int] = None,
        model: Optional[str] = None,
    ) -> None:
        super().__init__(
            ip, token, start_id, debug, lazy_discover, timeout=timeout, model=model
        )

        self._model_info = Yeelight._spec_helper.get_model_info(self.model)
        self._light_type = YeelightSubLightType.Main
        self._light_info = self._model_info.lamps[self._light_type]

    @command()
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

    @property
    def color_temperature_range(self) -> ValidSettingRange:
        """Return supported color temperature range."""
        return self._light_info.color_temp

    @command(
        click.option("--transition", type=int, required=False, default=0),
        click.option("--mode", type=int, required=False, default=0),
        default_output=format_output("Powering on"),
    )
    def on(self, transition=0, mode=0):
        """Power on.

        set_power ["on|off", "sudden|smooth", time_in_ms, mode]
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

    def set_power(self, on: bool, **kwargs):
        """Set power on or off."""
        if on:
            self.on(**kwargs)
        else:
            self.off(**kwargs)

    @command(
        click.argument("level", type=int),
        click.option("--transition", type=int, required=False, default=0),
        default_output=format_output("Setting brightness to {level}"),
    )
    def set_brightness(self, level, transition=0):
        """Set brightness."""
        if level < 0 or level > 100:
            raise ValueError("Invalid brightness: %s" % level)
        if transition > 0:
            return self.send("set_bright", [level, "smooth", transition])
        return self.send("set_bright", [level])

    @command(
        click.argument("level", type=int),
        click.option("--transition", type=int, required=False, default=0),
        default_output=format_output("Setting color temperature to {level}"),
    )
    def set_color_temp(self, level, transition=500):
        """Deprecated, use set_color_temperature instead."""
        _LOGGER.warning("Deprecated, use set_color_temperature instead.")
        self.set_color_temperature(level, transition)

    @command(
        click.argument("level", type=int),
        click.option("--transition", type=int, required=False, default=0),
        default_output=format_output("Setting color temperature to {level}"),
    )
    def set_color_temperature(self, level, transition=500):
        """Set color temp in kelvin."""
        if (
            level > self.color_temperature_range.max_value
            or level < self.color_temperature_range.min_value
        ):
            raise ValueError("Invalid color temperature: %s" % level)
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
                raise ValueError("Invalid color: %s" % color)

        return self.set_rgb_int(rgb_to_int(rgb))

    def set_rgb_int(self, rgb: int):
        """Set color from single RGB integer."""
        return self.send("set_rgb", [rgb])

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
    @action("Toggle")
    def toggle(self, *args):
        """Toggle bulb state."""
        return self.send("toggle")

    @command(default_output=format_output("Setting current settings to default"))
    @action("Set current as default")
    def set_default(self):
        """Set current state as default."""
        return self.send("set_default")

    @command(click.argument("table", default="evtRuleTbl"))
    def dump_ble_debug(self, table):
        """Dump the BLE debug table, defaults to evtRuleTbl.

        Some Yeelight devices offer support for BLE remotes.
        This command allows dumping the information about paired remotes,
        that can be used to decrypt the beacon payloads from these devices.

        Example:

        [{'mac': 'xxx', 'evtid': 4097, 'pid': 950, 'beaconkey': 'xxx'},
         {'mac': 'xxx', 'evtid': 4097, 'pid': 339, 'beaconkey': 'xxx'}]
        """
        return self.send("ble_dbg_tbl_dump", {"table": table})

    def set_scene(self, scene, *vals):
        """Set the scene."""
        raise NotImplementedError("Setting the scene is not implemented yet.")
        # return self.send("set_scene", [scene, *vals])
