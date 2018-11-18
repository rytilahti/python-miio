import logging
from collections import defaultdict
from typing import Any, Dict, Tuple

import click

from .click_common import command, format_output
from .device import Device, DeviceException
from .utils import int_to_rgb, rgb_to_int

_LOGGER = logging.getLogger(__name__)


class PhilipsMoonlightException(DeviceException):
    pass


class PhilipsMoonlightStatus:
    """Container for status reports from Xiaomi Philips Zhirui Bedside Lamp."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Moonlight (philips.light.moonlight):

        {'pow': 'off', 'sta': 0, 'bri': 1, 'rgb': 16741971, 'cct': 1, 'snm': 0, 'spr': 0,
         'spt': 15, 'wke': 0, 'bl': 1, 'ms': 1, 'mb': 1, 'wkp': [0, 24, 0]}
        """
        self.data = data

    @property
    def power(self) -> str:
        return self.data["pow"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def brightness(self) -> int:
        return self.data["bri"]

    @property
    def color_temperature(self) -> int:
        return self.data["cct"]

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Return color in RGB."""
        return int_to_rgb(int(self.data["rgb"]))

    @property
    def scene(self) -> int:
        return self.data["snm"]

    @property
    def sleep_assistant(self) -> int:
        """
        Example values:

        0: Unknown
        1: Unknown
        2: Sleep assistant enabled
        3: Awake
        """
        return self.data["sta"]

    @property
    def sleep_off_time(self) -> int:
        return self.data["spr"]

    @property
    def total_assistant_sleep_time(self) -> int:
        return self.data["spt"]

    @property
    def brand_sleep(self) -> bool:
        # sp_sleep_open?
        return self.data["ms"] == 1

    @property
    def brand(self) -> bool:
        # sp_xm_bracelet?
        return self.data["mb"] == 1

    @property
    def wake_up_time(self) -> [int, int, int]:
        # Example: [weekdays?, hour, minute]
        return self.data["wkp"]

    def __repr__(self) -> str:
        s = "<PhilipsMoonlightStatus power=%s, " \
            "brightness=%s, " \
            "color_temperature=%s, " \
            "rgb=%s, " \
            "scene=%s>" % \
            (self.power,
             self.brightness,
             self.color_temperature,
             self.rgb,
             self.scene)
        return s

    def __json__(self):
        return self.data


class PhilipsMoonlight(Device):
    """Main class representing Xiaomi Philips Zhirui Bedside Lamp.

    Not yet implemented features/methods:

    add_mb                          # Add miband
    get_band_period                 # Bracelet work time
    get_mb_rssi                     # Miband RSSI
    get_mb_mac                      # Miband MAC address
    enable_mibs
    set_band_period
    miIO.bleStartSearchBand
    miIO.bleGetNearbyBandList

    enable_sub_voice                # Sub voice control?
    enable_voice                    # Voice control

    skip_breath
    set_sleep_time
    set_wakeup_time
    en_sleep
    en_wakeup
    go_night                        # Night light / read mode
    get_wakeup_time
    enable_bl                       # Night light

    """

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Brightness: {result.brightness}\n"
            "Color temperature: {result.color_temperature}\n"
            "RGB: {result.rgb}\n"
            "Scene: {result.scene}\n"
        )
    )
    def status(self) -> PhilipsMoonlightStatus:
        """Retrieve properties."""
        properties = ['pow', 'sta', 'bri', 'rgb', 'cct', 'snm', 'spr', 'spt', 'wke', 'bl', 'ms',
                      'mb', 'wkp']
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

        return PhilipsMoonlightStatus(
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
        click.argument("rgb", default=[255] * 3, type=click.Tuple([int, int, int])),
        default_output=format_output("Setting color to {rgb}")
    )
    def set_rgb(self, rgb: Tuple[int, int, int]):
        """Set color in RGB."""
        for color in rgb:
            if color < 0 or color > 255:
                raise PhilipsMoonlightException("Invalid color: %s" % color)

        return self.send("set_rgb", [rgb_to_int(rgb)])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}")
    )
    def set_brightness(self, level: int):
        """Set brightness level."""
        if level < 1 or level > 100:
            raise PhilipsMoonlightException("Invalid brightness: %s" % level)

        return self.send("set_bright", [level])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting color temperature to {level}")
    )
    def set_color_temperature(self, level: int):
        """Set Correlated Color Temperature."""
        if level < 1 or level > 100:
            raise PhilipsMoonlightException("Invalid color temperature: %s" % level)

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
            raise PhilipsMoonlightException("Invalid brightness: %s" % brightness)

        if cct < 1 or cct > 100:
            raise PhilipsMoonlightException("Invalid color temperature: %s" % cct)

        return self.send("set_bricct", [brightness, cct])

    @command(
        click.argument("brightness", type=int),
        click.argument("rgb", type=int),
        default_output=format_output(
            "Setting brightness to {brightness} and color to {rgb}")
    )
    def set_brightness_and_rgb(self, brightness: int, rgb: int):
        """Set brightness level and the color."""
        if brightness < 1 or brightness > 100:
            raise PhilipsMoonlightException("Invalid brightness: %s" % brightness)

        if rgb < 0 or rgb > 16777215:
            raise PhilipsMoonlightException("Invalid color: %s" % rgb)

        return self.send("set_brirgb", [brightness, rgb])

    @command(
        click.argument("number", type=int),
        default_output=format_output("Setting fixed scene to {number}")
    )
    def set_scene(self, number: int):
        """Set scene number."""
        if number < 1 or number > 4:
            raise PhilipsMoonlightException("Invalid fixed scene number: %s" % number)

        return self.send("apply_fixed_scene", [number])
