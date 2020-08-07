"""Xiaomi Zigbee remote switches/buttons."""

from .subdevice import SubDevice


class RemoteSwitchDevice(SubDevice):
    """Base class for subdevice remote switch/button."""

    properties = []


class RemoteSwitchDoubleV1(RemoteSwitchDevice):
    """Subdevice RemoteSwitchDoubleV1 specific properties and methods."""

    _zigbee_model = "lumi.sensor_86sw2.v1"
    _model = "WXKG02LM 2016"
    _name = "Remote switch double"


class RemoteSwitchSingleV1(RemoteSwitchDevice):
    """Subdevice RemoteSwitchSingleV1 specific properties and methods."""

    _zigbee_model = "lumi.sensor_86sw1.v1"
    _model = "WXKG03LM 2016"
    _name = "Remote switch single"


class RemoteSwitchSingle(RemoteSwitchDevice):
    """Subdevice RemoteSwitchSingle specific properties and methods."""

    _zigbee_model = "lumi.remote.b186acn01"
    _model = "WXKG03LM 2018"
    _name = "Remote switch single"


class RemoteSwitchDouble(RemoteSwitchDevice):
    """Subdevice RemoteSwitchDouble specific properties and methods."""

    _zigbee_model = "lumi.remote.b286acn01"
    _model = "WXKG02LM 2018"
    _name = "Remote switch double"


class D1RemoteSwitchSingle(RemoteSwitchDevice):
    """Subdevice D1RemoteSwitchSingle specific properties and methods."""

    _zigbee_model = "lumi.remote.b186acn02"
    _model = "WXKG06LM"
    _name = "D1 remote switch single"


class D1RemoteSwitchDouble(RemoteSwitchDevice):
    """Subdevice D1RemoteSwitchDouble specific properties and methods."""

    _zigbee_model = "lumi.remote.b286acn02"
    _model = "WXKG07LM"
    _name = "D1 remote switch double"


class Switch(RemoteSwitchDevice):
    """Subdevice Switch specific properties and methods."""

    _zigbee_model = "lumi.sensor_switch"
    _model = "WXKG01LM"
    _name = "Button"


class AqaraSwitch(RemoteSwitchDevice):
    """Subdevice AqaraSwitch specific properties and methods."""

    _zigbee_model = "lumi.sensor_switch.aq2"
    _model = "WXKG11LM 2015"
    _name = "Button"


class AqaraSquareButtonV3(RemoteSwitchDevice):
    """Subdevice AqaraSquareButtonV3 specific properties and methods."""

    _zigbee_model = "lumi.sensor_switch.aq3"
    _model = "WXKG12LM"
    _name = "Button"


class AqaraSquareButton(RemoteSwitchDevice):
    """Subdevice AqaraSquareButton specific properties and methods."""

    _zigbee_model = "lumi.remote.b1acn01"
    _model = "WXKG11LM 2018"
    _name = "Button"
