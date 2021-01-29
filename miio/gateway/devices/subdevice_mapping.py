from enum import IntEnum

class DeviceType(IntEnum):
    """DeviceType matching using the values provided by Xiaomi."""

    Gateway = 0  # lumi.0
    Switch = 1  # lumi.sensor_switch
    Motion = 2  # lumi.sensor_motion
    
    SwitchTwoChannels = 7  # lumi.ctrl_neutral2
    
    SwitchOneChannel = 9  # lumi.ctrl_neutral1.v1
    Plug = 11  # lumi.plug
    RemoteSwitchDoubleV1 = 12  # lumi.sensor_86sw2.v1
    
    RemoteSwitchSingleV1 = 14  # lumi.sensor_86sw1.v1
    SensorSmoke = 15  # lumi.sensor_smoke
    AqaraWallOutletV1 = 17  # lumi.ctrl_86plug.v1
    SensorNatgas = 18  # lumi.sensor_natgas
    SwitchLiveOneChannel = 20  # lumi.ctrl_ln1
    SwitchLiveTwoChannels = 21  # lumi.ctrl_ln2
    AqaraSwitch = 51  # lumi.sensor_switch.aq2
    AqaraMotion = 52  # lumi.sensor_motion.aq2
    
    AqaraRelayTwoChannels = 54  # lumi.relay.c2acn01
    AqaraWaterLeak = 55  # lumi.sensor_wleak.aq1
    AqaraVibration = 56  # lumi.vibration.aq1
    DoorLockS1 = 59  # lumi.lock.aq1
    AqaraSquareButtonV3 = 62  # lumi.sensor_switch.aq3
    AqaraSwitchOneChannel = 63  # lumi.ctrl_ln1.aq1
    AqaraSwitchTwoChannels = 64  # lumi.ctrl_ln2.aq1
    AqaraWallOutlet = 65  # lumi.ctrl_86plug.aq1
    
    
    LockS2 = 70  # lumi.lock.acn02
    
    
    LockV1 = 81  # lumi.lock.v1

    AqaraSquareButton = 133  # lumi.remote.b1acn01
    RemoteSwitchSingle = 134  # lumi.remote.b186acn01
    RemoteSwitchDouble = 135  # lumi.remote.b286acn01
    LockS2Pro = 163  # lumi.lock.acn03
    D1RemoteSwitchSingle = 171  # lumi.remote.b186acn02
    D1RemoteSwitchDouble = 172  # lumi.remote.b286acn02
    D1WallSwitchTriple = 176  # lumi.switch.n3acn3
    D1WallSwitchTripleNN = 177  # lumi.switch.l3acn3
    ThermostatS2 = 207  # lumi.airrtc.tcpecn02



