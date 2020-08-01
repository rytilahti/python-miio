"""Xiaomi Zigbee curtain."""

from .sub_device import SubDevice


class CurtainV1(SubDevice):
    """Subdevice CurtainV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.curtain"
    _model = "ZNCLDJ11LM"
    _name = "Curtain"


class Curtain(SubDevice):
    """Subdevice Curtain specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.curtain.aq2"
    _model = "ZNGZDJ11LM"
    _name = "Curtain"


class CurtainB1(SubDevice):
    """Subdevice CurtainB1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.curtain.hagl04"
    _model = "ZNCLDJ12LM"
    _name = "Curtain B1"
