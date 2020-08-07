"""Xiaomi Zigbee lights."""

import attr
import click

from ...click_common import command
from .subdevice import SubDevice


class LightBulb(SubDevice):
    """Base class for subdevice light bulbs."""

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        brightness: int = None  # in %
        color_temp: int = None  # cct value from _ctt_min to _ctt_max
        cct_min: int = 153
        cct_max: int = 500

    @command()
    def update(self):
        """Update all device properties."""
        self._props.brightness = self.send("get_bright").pop()
        self._props.color_temp = self.send("get_ct").pop()
        if self._props.brightness > 0 and self._props.brightness <= 100:
            self._props.status = "on"
        else:
            self._props.status = "off"

    @command()
    def on(self):
        """Turn bulb on."""
        return self.send_arg("set_power", ["on"]).pop()

    @command()
    def off(self):
        """Turn bulb off."""
        return self.send_arg("set_power", ["off"]).pop()

    @command(click.argument("ctt", type=int))
    def set_color_temp(self, ctt):
        """Set the color temperature of the bulb ctt_min-ctt_max."""
        return self.send_arg("set_ct", [ctt]).pop()

    @command(click.argument("brightness", type=int))
    def set_brightness(self, brightness):
        """Set the brightness of the bulb 1-100."""
        return self.send_arg("set_bright", [brightness]).pop()


class AqaraSmartBulbE27(LightBulb):
    """Subdevice AqaraSmartBulbE27 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.light.aqcn02"
    _model = "ZNLDP12LM"
    _name = "Smart bulb E27"


class IkeaBulb82(LightBulb):
    """Subdevice IkeaBulb82 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1545g12"
    _model = "LED1545G12"
    _name = "Ikea smart bulb E27 white"


class IkeaBulb83(LightBulb):
    """Subdevice IkeaBulb83 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1546g12"
    _model = "LED1546G12"
    _name = "Ikea smart bulb E27 white"


class IkeaBulb84(LightBulb):
    """Subdevice IkeaBulb84 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1536g5"
    _model = "LED1536G5"
    _name = "Ikea smart bulb E12 white"


class IkeaBulb85(LightBulb):
    """Subdevice IkeaBulb85 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1537r6"
    _model = "LED1537R6"
    _name = "Ikea smart bulb GU10 white"


class IkeaBulb86(LightBulb):
    """Subdevice IkeaBulb86 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1623g12"
    _model = "LED1623G12"
    _name = "Ikea smart bulb E27 white"


class IkeaBulb87(LightBulb):
    """Subdevice IkeaBulb87 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1650r5"
    _model = "LED1650R5"
    _name = "Ikea smart bulb GU10 white"


class IkeaBulb88(LightBulb):
    """Subdevice IkeaBulb88 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1649c5"
    _model = "LED1649C5"
    _name = "Ikea smart bulb E12 white"
