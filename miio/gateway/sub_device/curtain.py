"""Xiaomi Zigbee curtain."""

from .sub_device import SubDevice


class CurtainDevice(SubDevice):
    """Base class for subdevice curtain."""

    properties = []


class CurtainV1(CurtainDevice):
    """Subdevice CurtainV1 specific properties and methods."""

    _zigbee_model = "lumi.curtain"
    _model = "ZNCLDJ11LM"
    _name = "Curtain"


class Curtain(CurtainDevice):
    """Subdevice Curtain specific properties and methods."""

    _zigbee_model = "lumi.curtain.aq2"
    _model = "ZNGZDJ11LM"
    _name = "Curtain"


class CurtainB1(CurtainDevice):
    """Subdevice CurtainB1 specific properties and methods."""

    _zigbee_model = "lumi.curtain.hagl04"
    _model = "ZNCLDJ12LM"
    _name = "Curtain B1"
