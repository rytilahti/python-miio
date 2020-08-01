"""Xiaomi Zigbee switches."""

import attr

from ...click_common import command
from .sub_device import SubDevice


class SwitchTwoChannels(SubDevice):
    """Subdevice SwitchTwoChannels specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_neutral2"
    _model = "QBKG03LM"
    _name = "Wall switch double no neutral"


class SwitchOneChannel(SubDevice):
    """Subdevice SwitchOneChannel specific properties and methods."""

    properties = ["neutral_0"]
    _zigbee_model = "lumi.ctrl_neutral1.v1"
    _model = "QBKG04LM"
    _name = "Wall switch no neutral"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]

    @command()
    def toggle(self):
        """Toggle Switch One Channel."""
        return self.send_arg("toggle_ctrl_neutral", ["channel_0", "toggle"]).pop()

    @command()
    def on(self):
        """Turn on Switch One Channel."""
        return self.send_arg("toggle_ctrl_neutral", ["channel_0", "on"]).pop()

    @command()
    def off(self):
        """Turn off Switch One Channel."""
        return self.send_arg("toggle_ctrl_neutral", ["channel_0", "off"]).pop()


class SwitchLiveOneChannel(SubDevice):
    """Subdevice SwitchLiveOneChannel specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_ln1"
    _model = "QBKG11LM"
    _name = "Wall switch single"


class SwitchLiveTwoChannels(SubDevice):
    """Subdevice SwitchLiveTwoChannels specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_ln2"
    _model = "QBKG12LM"
    _name = "Wall switch double"


class AqaraSwitchOneChannel(SubDevice):
    """Subdevice AqaraSwitchOneChannel specific properties and methods."""

    properties = ["neutral_0", "load_power"]
    _zigbee_model = "lumi.ctrl_ln1.aq1"
    _model = "QBKG11LM"
    _name = "Wall switch single"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in ?unit?

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]
        self._props.load_power = values[1]


class AqaraSwitchTwoChannels(SubDevice):
    """Subdevice AqaraSwitchTwoChannels specific properties and methods."""

    properties = ["neutral_0", "neutral_1", "load_power"]
    _zigbee_model = "lumi.ctrl_ln2.aq1"
    _model = "QBKG12LM"
    _name = "Wall switch double"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in ?unit?

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status_ch0 = values[0]
        self._props.status_ch1 = values[1]
        self._props.load_power = values[2]


class D1WallSwitchTriple(SubDevice):
    """Subdevice D1WallSwitchTriple specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.switch.n3acn3"
    _model = "QBKG26LM"
    _name = "D1 wall switch triple"


class D1WallSwitchTripleNN(SubDevice):
    """Subdevice D1WallSwitchTripleNN specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.switch.l3acn3"
    _model = "QBKG25LM"
    _name = "D1 wall switch triple no neutral"


class Plug(SubDevice):
    """Subdevice Plug specific properties and methods."""

    accessor = "get_prop_plug"
    properties = ["neutral_0", "load_power"]
    _zigbee_model = "lumi.plug"
    _model = "ZNCZ02LM"
    _name = "Plug"

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
        """Toggle Plug."""
        return self.send_arg("toggle_plug", ["channel_0", "toggle"]).pop()

    @command()
    def on(self):
        """Turn on Plug."""
        return self.send_arg("toggle_plug", ["channel_0", "on"]).pop()

    @command()
    def off(self):
        """Turn off Plug."""
        return self.send_arg("toggle_plug", ["channel_0", "off"]).pop()
