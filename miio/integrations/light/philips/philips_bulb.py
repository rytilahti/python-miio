import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from miio import Device, DeviceStatus
from miio.click_common import command, format_output

_LOGGER = logging.getLogger(__name__)

MODEL_PHILIPS_LIGHT_BULB = "philips.light.bulb"
MODEL_PHILIPS_LIGHT_HBULB = "philips.light.hbulb"
MODEL_PHILIPS_LIGHT_CBULB = "philips.light.cbulb"
MODEL_PHILIPS_ZHIRUI_DOWNLIGHT = "philips.light.downlight"
MODEL_PHILIPS_CANDLE = "philips.light.candle"
MODEL_PHILIPS_CANDLE2 = "philips.light.candle2"

AVAILABLE_PROPERTIES_COMMON = ["power", "dv"]
AVAILABLE_PROPERTIES_COLORTEMP = AVAILABLE_PROPERTIES_COMMON + ["bright", "cct", "snm"]

AVAILABLE_PROPERTIES = {
    MODEL_PHILIPS_LIGHT_HBULB: AVAILABLE_PROPERTIES_COMMON + ["bri"],
    MODEL_PHILIPS_LIGHT_BULB: AVAILABLE_PROPERTIES_COLORTEMP,
    MODEL_PHILIPS_LIGHT_CBULB: AVAILABLE_PROPERTIES_COLORTEMP,
    MODEL_PHILIPS_ZHIRUI_DOWNLIGHT: AVAILABLE_PROPERTIES_COLORTEMP,
    MODEL_PHILIPS_CANDLE: AVAILABLE_PROPERTIES_COLORTEMP,
    MODEL_PHILIPS_CANDLE2: AVAILABLE_PROPERTIES_COLORTEMP,
}


class PhilipsBulbStatus(DeviceStatus):
    """Container for status reports from Xiaomi Philips LED Ceiling Lamp."""

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
    def brightness(self) -> Optional[int]:
        if "bright" in self.data:
            return self.data["bright"]
        if "bri" in self.data:
            return self.data["bri"]
        return None

    @property
    def color_temperature(self) -> Optional[int]:
        if "cct" in self.data:
            return self.data["cct"]
        return None

    @property
    def scene(self) -> Optional[int]:
        if "snm" in self.data:
            return self.data["snm"]
        return None

    @property
    def delay_off_countdown(self) -> int:
        return self.data["dv"]


class PhilipsWhiteBulb(Device):
    """Main class representing Xiaomi Philips White LED Ball Lamp."""

    _supported_models = [MODEL_PHILIPS_LIGHT_HBULB]

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Brightness: {result.brightness}\n"
            "Delayed turn off: {result.delay_off_countdown}\n"
            "Color temperature: {result.color_temperature}\n"
            "Scene: {result.scene}\n",
        )
    )
    def status(self) -> PhilipsBulbStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_PHILIPS_LIGHT_BULB]
        )
        values = self.get_properties(properties)

        return PhilipsBulbStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}"),
    )
    def set_brightness(self, level: int):
        """Set brightness level."""
        if level < 1 or level > 100:
            raise ValueError("Invalid brightness: %s" % level)

        return self.send("set_bright", [level])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds"),
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""

        if seconds < 1:
            raise ValueError("Invalid value for a delayed turn off: %s" % seconds)

        return self.send("delay_off", [seconds])


class PhilipsBulb(PhilipsWhiteBulb):
    """Support for philips bulbs that support color temperature and scenes."""

    _supported_models = list(AVAILABLE_PROPERTIES.keys())

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting color temperature to {level}"),
    )
    def set_color_temperature(self, level: int):
        """Set Correlated Color Temperature."""
        if level < 1 or level > 100:
            raise ValueError("Invalid color temperature: %s" % level)

        return self.send("set_cct", [level])

    @command(
        click.argument("brightness", type=int),
        click.argument("cct", type=int),
        default_output=format_output(
            "Setting brightness to {brightness} and color temperature to {cct}"
        ),
    )
    def set_brightness_and_color_temperature(self, brightness: int, cct: int):
        """Set brightness level and the correlated color temperature."""
        if brightness < 1 or brightness > 100:
            raise ValueError("Invalid brightness: %s" % brightness)

        if cct < 1 or cct > 100:
            raise ValueError("Invalid color temperature: %s" % cct)

        return self.send("set_bricct", [brightness, cct])

    @command(
        click.argument("number", type=int),
        default_output=format_output("Setting fixed scene to {number}"),
    )
    def set_scene(self, number: int):
        """Set scene number."""
        if number < 1 or number > 4:
            raise ValueError("Invalid fixed scene number: %s" % number)

        return self.send("apply_fixed_scene", [number])
