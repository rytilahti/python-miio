"""Xiaomi Zigbee buttons."""

from .sub_device import SubDevice


class Switch(SubDevice):
    """Subdevice Switch specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_switch"
    _model = "WXKG01LM"
    _name = "Button"


class AqaraSwitch(SubDevice):
    """Subdevice AqaraSwitch specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_switch.aq2"
    _model = "WXKG11LM 2015"
    _name = "Button"


class AqaraSquareButtonV3(SubDevice):
    """Subdevice AqaraSquareButtonV3 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_switch.aq3"
    _model = "WXKG12LM"
    _name = "Button"


class AqaraSquareButton(SubDevice):
    """Subdevice AqaraSquareButton specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.remote.b1acn01"
    _model = "WXKG11LM 2018"
    _name = "Button"
