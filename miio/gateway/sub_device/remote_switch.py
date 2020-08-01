"""Xiaomi Zigbee remote switches."""

from .sub_device import SubDevice


class RemoteSwitchDoubleV1(SubDevice):
    """Subdevice RemoteSwitchDoubleV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_86sw2.v1"
    _model = "WXKG02LM 2016"
    _name = "Remote switch double"


class RemoteSwitchSingleV1(SubDevice):
    """Subdevice RemoteSwitchSingleV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_86sw1.v1"
    _model = "WXKG03LM 2016"
    _name = "Remote switch single"


class RemoteSwitchSingle(SubDevice):
    """Subdevice RemoteSwitchSingle specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.remote.b186acn01"
    _model = "WXKG03LM 2018"
    _name = "Remote switch single"


class RemoteSwitchDouble(SubDevice):
    """Subdevice RemoteSwitchDouble specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.remote.b286acn01"
    _model = "WXKG02LM 2018"
    _name = "Remote switch double"


class D1RemoteSwitchSingle(SubDevice):
    """Subdevice D1RemoteSwitchSingle specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.remote.b186acn02"
    _model = "WXKG06LM"
    _name = "D1 remote switch single"


class D1RemoteSwitchDouble(SubDevice):
    """Subdevice D1RemoteSwitchDouble specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.remote.b286acn02"
    _model = "WXKG07LM"
    _name = "D1 remote switch double"
