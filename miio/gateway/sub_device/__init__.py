"""Xiaomi Gateway subdevice base class."""

from .button import AqaraSquareButton, AqaraSquareButtonV3, AqaraSwitch, Switch
from .cube import Cube, CubeV2
from .curtain import Curtain, CurtainB1, CurtainV1
from .door_sensor import AqaraMagnet, Magnet
from .light import (
    AqaraSmartBulbE27,
    IkeaBulb82,
    IkeaBulb83,
    IkeaBulb84,
    IkeaBulb85,
    IkeaBulb86,
    IkeaBulb87,
    IkeaBulb88,
)
from .lock import DoorLockS1, LockS2, LockS2Pro, LockV1
from .motion_sensor import AqaraMotion, Motion
from .remote_switch import (
    D1RemoteSwitchDouble,
    D1RemoteSwitchSingle,
    RemoteSwitchDouble,
    RemoteSwitchDoubleV1,
    RemoteSwitchSingle,
    RemoteSwitchSingleV1,
)
from .sensor import AqaraVibration, AqaraWaterLeak, SensorNatgas, SensorSmoke
from .sub_device import SubDevice, SubDeviceInfo
from .switch import (
    AqaraSwitchOneChannel,
    AqaraSwitchTwoChannels,
    D1WallSwitchTriple,
    D1WallSwitchTripleNN,
    Plug,
    SwitchLiveOneChannel,
    SwitchLiveTwoChannels,
    SwitchOneChannel,
    SwitchTwoChannels,
)
from .thermostat import ThermostatS2
from .wall_outlet import AqaraRelayTwoChannels, AqaraWallOutlet, AqaraWallOutletV1
from .weather_sensor import AqaraHT, SensorHT
