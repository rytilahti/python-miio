"""Xiaomi Zigbee switches."""

from enum import IntEnum

import click

from ...click_common import command
from .subdevice import SubDevice


class Switch(SubDevice):
    """Base class for one channel switch subdevice that supports on/off."""

    class ChannelMap(IntEnum):
        """Option to select wich channel to control."""

        channel_0 = 0
        channel_1 = 1
        channel_2 = 2

    @command(click.argument("channel", type=int))
    def toggle(self, channel: int = 0):
        """Toggle a channel of the switch, default channel_0."""
        return self.send_arg(
            self.setter, [self.ChannelMap(channel).name, "toggle"]
        ).pop()

    @command(click.argument("channel", type=int))
    def on(self, channel: int = 0):
        """Turn on a channel of the switch, default channel_0."""
        return self.send_arg(self.setter, [self.ChannelMap(channel).name, "on"]).pop()

    @command(click.argument("channel", type=int))
    def off(self, channel: int = 0):
        """Turn off a channel of the switch, default channel_0."""
        return self.send_arg(self.setter, [self.ChannelMap(channel).name, "off"]).pop()
