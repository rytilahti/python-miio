"""Xiaomi Zigbee switches."""

from enum import IntEnum

import attr
import click

from ...click_common import command
from .sub_device import SubDevice


class OneChannelSwitch(SubDevice):
    """Base class for one channel switch subdevice that supports on/off."""

    properties = ["neutral_0"]
    set_command = "toggle_ctrl_neutral"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]

    class Channel_map(IntEnum):
        """Option to select wich channel to control."""

        channel_0 = 0
        channel_1 = 1
        channel_2 = 2

    @command(click.argument("channel", type=int))
    def toggle(self, channel: int = 0):
        """Toggle a channel of the switch, default channel_0."""
        return self.send_arg(self.set_command, [self.Channel_map(channel).name, "toggle"]).pop()

    @command(click.argument("channel", type=int))
    def on(self, channel: int = 0):
        """Turn on a channel of the switch, default channel_0."""
        return self.send_arg(self.set_command, [self.Channel_map(channel).name, "on"]).pop()

    @command(click.argument("channel", type=int))
    def off(self, channel: int = 0):
        """Turn off a channel of the switch, default channel_0."""
        return self.send_arg(self.set_command, [self.Channel_map(channel).name, "off"]).pop()


class TwoChannelSwitch(OneChannelSwitch):
    """Base class for two channel switch subdevice that supports on/off."""

    properties = ["neutral_0", "neutral_1"]

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status_ch0 = values[0]
        self._props.status_ch1 = values[1]


class OneChannelSwitchLoad(OneChannelSwitch):
    """Base class for one channel switch subdevice that supports on/off and load_power."""

    properties = ["neutral_0", "load_power"]

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


class TwoChannelSwitchLoad(OneChannelSwitch):
    """Base class for two channel switch subdevice that supports on/off and load_power."""

    properties = ["neutral_0", "neutral_1", "load_power"]

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in Watt

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status_ch0 = values[0]
        self._props.status_ch1 = values[1]
        self._props.load_power = values[2]


class ThreeChannelSwitchLoad(OneChannelSwitch):
    """Base class for three channel switch subdevice that supports on/off and load_power."""

    properties = ["neutral_0", "neutral_1", "neutral_2", "load_power"]

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'
        status_ch2: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in Watt

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status_ch0 = values[0]
        self._props.status_ch1 = values[1]
        self._props.status_ch2 = values[2]
        self._props.load_power = values[3]


class SwitchTwoChannels(TwoChannelSwitch):
    """Subdevice SwitchTwoChannels specific properties and methods."""

    _zigbee_model = "lumi.ctrl_neutral2"
    _model = "QBKG03LM"
    _name = "Wall switch double no neutral"


class SwitchOneChannel(OneChannelSwitch):
    """Subdevice SwitchOneChannel specific properties and methods."""

    _zigbee_model = "lumi.ctrl_neutral1.v1"
    _model = "QBKG04LM"
    _name = "Wall switch no neutral"


class SwitchLiveOneChannel(OneChannelSwitchLoad):
    """Subdevice SwitchLiveOneChannel specific properties and methods."""

    _zigbee_model = "lumi.ctrl_ln1"
    _model = "QBKG11LM"
    _name = "Wall switch single"


class SwitchLiveTwoChannels(TwoChannelSwitchLoad):
    """Subdevice SwitchLiveTwoChannels specific properties and methods."""

    _zigbee_model = "lumi.ctrl_ln2"
    _model = "QBKG12LM"
    _name = "Wall switch double"


class AqaraSwitchOneChannel(OneChannelSwitchLoad):
    """Subdevice AqaraSwitchOneChannel specific properties and methods."""

    _zigbee_model = "lumi.ctrl_ln1.aq1"
    _model = "QBKG11LM"
    _name = "Wall switch single"


class AqaraSwitchTwoChannels(TwoChannelSwitchLoad):
    """Subdevice AqaraSwitchTwoChannels specific properties and methods."""

    _zigbee_model = "lumi.ctrl_ln2.aq1"
    _model = "QBKG12LM"
    _name = "Wall switch double"


class D1WallSwitchTriple(ThreeChannelSwitchLoad):
    """Subdevice D1WallSwitchTriple specific properties and methods."""

    _zigbee_model = "lumi.switch.n3acn3"
    _model = "QBKG26LM"
    _name = "D1 wall switch triple"


class D1WallSwitchTripleNN(ThreeChannelSwitchLoad):
    """Subdevice D1WallSwitchTripleNN specific properties and methods."""

    _zigbee_model = "lumi.switch.l3acn3"
    _model = "QBKG25LM"
    _name = "D1 wall switch triple no neutral"


class Plug(OneChannelSwitchLoad):
    """Subdevice Plug specific properties and methods."""

    accessor = "get_prop_plug"
    set_command = "toggle_plug"
    _zigbee_model = "lumi.plug"
    _model = "ZNCZ02LM"
    _name = "Plug"


class AqaraWallOutletV1(OneChannelSwitch):
    """Subdevice AqaraWallOutletV1 specific properties and methods."""

    properties = ["channel_0"]
    set_command = "toggle_plug"
    _zigbee_model = "lumi.ctrl_86plug.v1"
    _model = "QBCZ11LM"
    _name = "Wall outlet"


class AqaraWallOutlet(OneChannelSwitchLoad):
    """Subdevice AqaraWallOutlet specific properties and methods."""

    properties = ["channel_0", "load_power"]
    set_command = "toggle_plug"
    _zigbee_model = "lumi.ctrl_86plug.aq1"
    _model = "QBCZ11LM"
    _name = "Wall outlet"


class AqaraRelayTwoChannels(TwoChannelSwitchLoad):
    """Subdevice AqaraRelayTwoChannels specific properties and methods."""

    properties = ["channel_0", "channel_1", "load_power"]
    _zigbee_model = "lumi.relay.c2acn01"
    _model = "LLKZMK11LM"
    _name = "Relay"
