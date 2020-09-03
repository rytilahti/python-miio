from enum import IntEnum

from . import (
    AqaraHT,
    AqaraMagnet,
    AqaraMotion,
    AqaraRelayTwoChannels,
    AqaraSmartBulbE27,
    AqaraSquareButton,
    AqaraSquareButtonV3,
    AqaraSwitch,
    AqaraSwitchOneChannel,
    AqaraSwitchTwoChannels,
    AqaraVibration,
    AqaraWallOutlet,
    AqaraWallOutletV1,
    AqaraWaterLeak,
    Cube,
    CubeV2,
    Curtain,
    CurtainB1,
    CurtainV1,
    D1RemoteSwitchDouble,
    D1RemoteSwitchSingle,
    D1WallSwitchTriple,
    D1WallSwitchTripleNN,
    DoorLockS1,
    IkeaBulb82,
    IkeaBulb83,
    IkeaBulb84,
    IkeaBulb85,
    IkeaBulb86,
    IkeaBulb87,
    IkeaBulb88,
    LockS2,
    LockS2Pro,
    LockV1,
    Magnet,
    Motion,
    Plug,
    RemoteSwitchDouble,
    RemoteSwitchDoubleV1,
    RemoteSwitchSingle,
    RemoteSwitchSingleV1,
    SensorHT,
    SensorNatgas,
    SensorSmoke,
    Switch,
    SwitchLiveOneChannel,
    SwitchLiveTwoChannels,
    SwitchOneChannel,
    SwitchTwoChannels,
    ThermostatS2,
)


class DeviceType(IntEnum):
    """DeviceType matching using the values provided by Xiaomi."""

    Unknown = -1
    Gateway = 0  # lumi.0
    Switch = 1  # lumi.sensor_switch
    Motion = 2  # lumi.sensor_motion
    Magnet = 3  # lumi.sensor_magnet
    SwitchTwoChannels = 7  # lumi.ctrl_neutral2
    Cube = 8  # lumi.sensor_cube.v1
    SwitchOneChannel = 9  # lumi.ctrl_neutral1.v1
    SensorHT = 10  # lumi.sensor_ht
    Plug = 11  # lumi.plug
    RemoteSwitchDoubleV1 = 12  # lumi.sensor_86sw2.v1
    CurtainV1 = 13  # lumi.curtain
    RemoteSwitchSingleV1 = 14  # lumi.sensor_86sw1.v1
    SensorSmoke = 15  # lumi.sensor_smoke
    AqaraWallOutletV1 = 17  # lumi.ctrl_86plug.v1
    SensorNatgas = 18  # lumi.sensor_natgas
    AqaraHT = 19  # lumi.weather.v1
    SwitchLiveOneChannel = 20  # lumi.ctrl_ln1
    SwitchLiveTwoChannels = 21  # lumi.ctrl_ln2
    AqaraSwitch = 51  # lumi.sensor_switch.aq2
    AqaraMotion = 52  # lumi.sensor_motion.aq2
    AqaraMagnet = 53  # lumi.sensor_magnet.aq2
    AqaraRelayTwoChannels = 54  # lumi.relay.c2acn01
    AqaraWaterLeak = 55  # lumi.sensor_wleak.aq1
    AqaraVibration = 56  # lumi.vibration.aq1
    DoorLockS1 = 59  # lumi.lock.aq1
    AqaraSquareButtonV3 = 62  # lumi.sensor_switch.aq3
    AqaraSwitchOneChannel = 63  # lumi.ctrl_ln1.aq1
    AqaraSwitchTwoChannels = 64  # lumi.ctrl_ln2.aq1
    AqaraWallOutlet = 65  # lumi.ctrl_86plug.aq1
    AqaraSmartBulbE27 = 66  # lumi.light.aqcn02
    CubeV2 = 68  # lumi.sensor_cube.aqgl01
    LockS2 = 70  # lumi.lock.acn02
    Curtain = 71  # lumi.curtain.aq2
    CurtainB1 = 72  # lumi.curtain.hagl04
    LockV1 = 81  # lumi.lock.v1
    IkeaBulb82 = 82  # ikea.light.led1545g12
    IkeaBulb83 = 83  # ikea.light.led1546g12
    IkeaBulb84 = 84  # ikea.light.led1536g5
    IkeaBulb85 = 85  # ikea.light.led1537r6
    IkeaBulb86 = 86  # ikea.light.led1623g12
    IkeaBulb87 = 87  # ikea.light.led1650r5
    IkeaBulb88 = 88  # ikea.light.led1649c5
    AqaraSquareButton = 133  # lumi.remote.b1acn01
    RemoteSwitchSingle = 134  # lumi.remote.b186acn01
    RemoteSwitchDouble = 135  # lumi.remote.b286acn01
    LockS2Pro = 163  # lumi.lock.acn03
    D1RemoteSwitchSingle = 171  # lumi.remote.b186acn02
    D1RemoteSwitchDouble = 172  # lumi.remote.b286acn02
    D1WallSwitchTriple = 176  # lumi.switch.n3acn3
    D1WallSwitchTripleNN = 177  # lumi.switch.l3acn3
    ThermostatS2 = 207  # lumi.airrtc.tcpecn02


# 166 - lumi.lock.acn05
# 167 - lumi.switch.b1lacn02
# 168 - lumi.switch.b2lacn02
# 169 - lumi.switch.b1nacn02
# 170 - lumi.switch.b2nacn02
# 202 - lumi.dimmer.rgbegl01
# 203 - lumi.dimmer.c3egl01
# 204 - lumi.dimmer.cwegl01
# 205 - lumi.airrtc.vrfegl01
# 206 - lumi.airrtc.tcpecn01


# from https://github.com/aholstenson/miio/issues/26
DeviceTypeMapping = {
    DeviceType.Switch: Switch,
    DeviceType.Motion: Motion,
    DeviceType.Magnet: Magnet,
    DeviceType.SwitchTwoChannels: SwitchTwoChannels,
    DeviceType.Cube: Cube,
    DeviceType.SwitchOneChannel: SwitchOneChannel,
    DeviceType.SensorHT: SensorHT,
    DeviceType.Plug: Plug,
    DeviceType.RemoteSwitchDoubleV1: RemoteSwitchDoubleV1,
    DeviceType.CurtainV1: CurtainV1,
    DeviceType.RemoteSwitchSingleV1: RemoteSwitchSingleV1,
    DeviceType.SensorSmoke: SensorSmoke,
    DeviceType.AqaraWallOutletV1: AqaraWallOutletV1,
    DeviceType.SensorNatgas: SensorNatgas,
    DeviceType.AqaraHT: AqaraHT,
    DeviceType.SwitchLiveOneChannel: SwitchLiveOneChannel,
    DeviceType.SwitchLiveTwoChannels: SwitchLiveTwoChannels,
    DeviceType.AqaraSwitch: AqaraSwitch,
    DeviceType.AqaraMotion: AqaraMotion,
    DeviceType.AqaraMagnet: AqaraMagnet,
    DeviceType.AqaraRelayTwoChannels: AqaraRelayTwoChannels,
    DeviceType.AqaraWaterLeak: AqaraWaterLeak,
    DeviceType.AqaraVibration: AqaraVibration,
    DeviceType.DoorLockS1: DoorLockS1,
    DeviceType.AqaraSquareButtonV3: AqaraSquareButtonV3,
    DeviceType.AqaraSwitchOneChannel: AqaraSwitchOneChannel,
    DeviceType.AqaraSwitchTwoChannels: AqaraSwitchTwoChannels,
    DeviceType.AqaraWallOutlet: AqaraWallOutlet,
    DeviceType.AqaraSmartBulbE27: AqaraSmartBulbE27,
    DeviceType.CubeV2: CubeV2,
    DeviceType.LockS2: LockS2,
    DeviceType.Curtain: Curtain,
    DeviceType.CurtainB1: CurtainB1,
    DeviceType.LockV1: LockV1,
    DeviceType.IkeaBulb82: IkeaBulb82,
    DeviceType.IkeaBulb83: IkeaBulb83,
    DeviceType.IkeaBulb84: IkeaBulb84,
    DeviceType.IkeaBulb85: IkeaBulb85,
    DeviceType.IkeaBulb86: IkeaBulb86,
    DeviceType.IkeaBulb87: IkeaBulb87,
    DeviceType.IkeaBulb88: IkeaBulb88,
    DeviceType.AqaraSquareButton: AqaraSquareButton,
    DeviceType.RemoteSwitchSingle: RemoteSwitchSingle,
    DeviceType.RemoteSwitchDouble: RemoteSwitchDouble,
    DeviceType.LockS2Pro: LockS2Pro,
    DeviceType.D1RemoteSwitchSingle: D1RemoteSwitchSingle,
    DeviceType.D1RemoteSwitchDouble: D1RemoteSwitchDouble,
    DeviceType.D1WallSwitchTriple: D1WallSwitchTriple,
    DeviceType.D1WallSwitchTripleNN: D1WallSwitchTripleNN,
    DeviceType.ThermostatS2: ThermostatS2,
}
