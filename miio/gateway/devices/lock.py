"""Xiaomi Zigbee Locks."""

from .subdevice import SubDevice


class LockDevice(SubDevice):
    """Base class for subdevice lock."""

    properties = []

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'locked' / 'unlocked'


class DoorLockS1(LockDevice):
    """Subdevice DoorLockS1 specific properties and methods."""

    _zigbee_model = "lumi.lock.aq1"
    _model = "ZNMS11LM"
    _name = "Door lock S1"


class LockS2(LockDevice):
    """Subdevice LockS2 specific properties and methods."""

    _zigbee_model = "lumi.lock.acn02"
    _model = "ZNMS12LM"
    _name = "Door lock S2"


class LockV1(LockDevice):
    """Subdevice LockV1 specific properties and methods."""

    _zigbee_model = "lumi.lock.v1"
    _model = "A6121"
    _name = "Vima cylinder lock"


class LockS2Pro(LockDevice):
    """Subdevice LockS2Pro specific properties and methods."""

    _zigbee_model = "lumi.lock.acn03"
    _model = "ZNMS13LM"
    _name = "Door lock S2 pro"
