"""Xiaomi Gateway subdevice base class."""

# flake8: noqa
from .light import LightBulb
from .lock import DoorLockS1, LockS2, LockS2Pro, LockV1
from .motion_sensor import AqaraMotion, Motion
from .remote_switch import (
    AqaraSquareButton,
    AqaraSquareButtonV3,
    AqaraSwitch,
    D1RemoteSwitchDouble,
    D1RemoteSwitchSingle,
    RemoteSwitchDouble,
    RemoteSwitchDoubleV1,
    RemoteSwitchSingle,
    RemoteSwitchSingleV1,
    Switch,
)
from .sensor import AqaraVibration, AqaraWaterLeak, SensorNatgas, SensorSmoke
from .switch import (
    AqaraRelayTwoChannels,
    AqaraSwitchOneChannel,
    AqaraSwitchTwoChannels,
    AqaraWallOutlet,
    AqaraWallOutletV1,
    D1WallSwitchTriple,
    D1WallSwitchTripleNN,
    Plug,
    SwitchLiveOneChannel,
    SwitchLiveTwoChannels,
    SwitchOneChannel,
    SwitchTwoChannels,
)
from .thermostat import ThermostatS2

from .subdevice import SubDevice, SubDeviceInfo  # isort:skip
from .subdevice_mapping import DeviceType  # isort:skip
