"""Xiaomi Zigbee Locks."""

from .sub_device import SubDevice


class DoorLockS1(SubDevice):
    """Subdevice DoorLockS1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.aq1"
    _model = "ZNMS11LM"
    _name = "Door lock S1"


class LockS2(SubDevice):
    """Subdevice LockS2 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.acn02"
    _model = "ZNMS12LM"
    _name = "Door lock S2"


class LockV1(SubDevice):
    """Subdevice LockV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.v1"
    _model = "A6121"
    _name = "Vima cylinder lock"


class LockS2Pro(SubDevice):
    """Subdevice LockS2Pro specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.acn03"
    _model = "ZNMS13LM"
    _name = "Door lock S2 pro"
