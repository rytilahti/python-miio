"""Xiaomi Zigbee wall outlets."""

from enum import Enum

import attr
import click

from ...click_common import EnumType, command
from .sub_device import SubDevice


class AqaraWallOutletV1(SubDevice):
    """Subdevice AqaraWallOutletV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_86plug.v1"
    _model = "QBCZ11LM"
    _name = "Wall outlet"


class AqaraWallOutlet(SubDevice):
    """Subdevice AqaraWallOutlet specific properties and methods."""

    properties = ["channel_0", "load_power"]
    _zigbee_model = "lumi.ctrl_86plug.aq1"
    _model = "QBCZ11LM"
    _name = "Wall outlet"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in Watt

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]
        self._props.load_power = values[1]

    @command()
    def toggle(self):
        """Toggle Aqara Wall Outlet."""
        return self.send_arg("toggle_plug", ["channel_0", "toggle"]).pop()

    @command()
    def on(self):
        """Turn on Aqara Wall Outlet."""
        return self.send_arg("toggle_plug", ["channel_0", "on"]).pop()

    @command()
    def off(self):
        """Turn off Aqara Wall Outlet."""
        return self.send_arg("toggle_plug", ["channel_0", "off"]).pop()


class AqaraRelayTwoChannels(SubDevice):
    """Subdevice AqaraRelayTwoChannels specific properties and methods."""

    properties = ["load_power", "channel_0", "channel_1"]
    _zigbee_model = "lumi.relay.c2acn01"
    _model = "LLKZMK11LM"
    _name = "Relay"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in ?unit?

    class AqaraRelayToggleValue(Enum):
        """Options to control the relay."""

        toggle = "toggle"
        on = "on"
        off = "off"

    class AqaraRelayChannel(Enum):
        """Options to select wich relay to control."""

        first = "channel_0"
        second = "channel_1"

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.load_power = values[0]
        self._props.status_ch0 = values[1]
        self._props.status_ch1 = values[2]

    @command(
        click.argument("channel", type=EnumType(AqaraRelayChannel)),
        click.argument("value", type=EnumType(AqaraRelayToggleValue)),
    )
    def toggle(self, channel, value):
        """Toggle Aqara Wireless Relay 2ch."""
        return self.send_arg("toggle_ctrl_neutral", [channel.value, value.value]).pop()
