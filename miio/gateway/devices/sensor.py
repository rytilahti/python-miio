"""Xiaomi Zigbee sensors."""

import click

from ...click_common import command
from .subdevice import SubDevice


class Vibration(SubDevice):
    """Base class for subdevice vibration sensor."""

    @command(click.argument("vibration_level", type=int))
    def set_vibration_sensitivity(self, vibration_level):
        """Set the sensitivity of the vibration sensor, low = 21, medium = 11, high = 1."""
        return self.set_property("vibration_level", vibration_level).pop()
