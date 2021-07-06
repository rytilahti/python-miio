"""Xiaomi Zigbee lights."""

import click

from ...click_common import command
from .subdevice import SubDevice


class LightBulb(SubDevice):
    """Base class for subdevice light bulbs."""

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
