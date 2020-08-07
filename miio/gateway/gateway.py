"""Xiaomi Gateway implementation using Miio protecol."""

import logging
from enum import IntEnum

import click

from ..click_common import command
from ..device import Device
from ..exceptions import DeviceError, DeviceException

_LOGGER = logging.getLogger(__name__)

GATEWAY_MODEL_CHINA = "lumi.gateway.v3"
GATEWAY_MODEL_EU = "lumi.gateway.mieu01"
GATEWAY_MODEL_ZIG3 = "lumi.gateway.mgl03"
GATEWAY_MODEL_AQARA = "lumi.gateway.aqhm01"
GATEWAY_MODEL_AC_V1 = "lumi.acpartner.v1"
GATEWAY_MODEL_AC_V2 = "lumi.acpartner.v2"
GATEWAY_MODEL_AC_V3 = "lumi.acpartner.v3"


class GatewayException(DeviceException):
    """Exception for the Xioami Gateway communication."""


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


class Gateway(Device):
    """Main class representing the Xiaomi Gateway.

    Use the given property getters to access specific functionalities such
    as `alarm` (for alarm controls) or `light` (for lights).

    Commands whose functionality or parameters are unknown,
    feel free to implement!
    * toggle_device
    * toggle_plug
    * remove_all_bind
    * list_bind [0]
    * bind_page
    * bind
    * remove_bind

    * self.get_prop("used_for_public") # Return the 'used_for_public' status, return value: [0] or [1], probably this has to do with developer mode.
    * self.set_prop("used_for_public", state) # Set the 'used_for_public' state, value: 0 or 1, probably this has to do with developer mode.

    * welcome
    * set_curtain_level

    * get_corridor_on_time
    * set_corridor_light ["off"]
    * get_corridor_light -> "on"

    * set_default_sound
    * set_doorbell_push, get_doorbell_push ["off"]
    * set_doorbell_volume [100], get_doorbell_volume
    * set_gateway_volume, get_gateway_volume
    * set_clock_volume
    * set_clock
    * get_sys_data
    * update_neighbor_token [{"did":x, "token":x, "ip":x}]

    ## property getters
    * ctrl_device_prop
    * get_device_prop_exp [[sid, list, of, properties]]

    ## scene
    * get_lumi_bind ["scene", <page number>] for rooms/devices"""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        from . import (
            Alarm,
            Radio,
            Zigbee,
            Light,
        )

        self._alarm = Alarm(parent=self)
        self._radio = Radio(parent=self)
        self._zigbee = Zigbee(parent=self)
        self._light = Light(parent=self)
        self._devices = {}
        self._info = None

    @property
    def alarm(self) -> "GatewayAlarm":  # noqa: F821
        """Return alarm control interface."""
        # example: gateway.alarm.on()
        return self._alarm

    @property
    def radio(self) -> "GatewayRadio":  # noqa: F821
        """Return radio control interface."""
        return self._radio

    @property
    def zigbee(self) -> "GatewayZigbee":  # noqa: F821
        """Return zigbee control interface."""
        return self._zigbee

    @property
    def light(self) -> "GatewayLight":  # noqa: F821
        """Return light control interface."""
        return self._light

    @property
    def devices(self):
        """Return a dict of the already discovered devices."""
        return self._devices

    @property
    def model(self):
        """Return the zigbee model of the gateway."""
        # Check if catch already has the gateway info, otherwise get it from the device
        if self._info is None:
            self._info = self.info()
        return self._info.model

    @command()
    def discover_devices(self):
        """
        Discovers SubDevices
        and returns a list of the discovered devices.
        """

        from .devices import (
            SubDevice,
            SubDeviceInfo,
            Switch,
            AqaraSwitch,
            AqaraSquareButtonV3,
            AqaraSquareButton,
            Cube,
            CubeV2,
            CurtainV1,
            Curtain,
            CurtainB1,
            Magnet,
            AqaraMagnet,
            AqaraSmartBulbE27,
            IkeaBulb82,
            IkeaBulb83,
            IkeaBulb84,
            IkeaBulb85,
            IkeaBulb86,
            IkeaBulb87,
            IkeaBulb88,
            DoorLockS1,
            LockS2,
            LockV1,
            LockS2Pro,
            Motion,
            AqaraMotion,
            RemoteSwitchDoubleV1,
            RemoteSwitchSingleV1,
            RemoteSwitchSingle,
            RemoteSwitchDouble,
            D1RemoteSwitchSingle,
            D1RemoteSwitchDouble,
            SensorSmoke,
            SensorNatgas,
            AqaraWaterLeak,
            AqaraVibration,
            SwitchTwoChannels,
            SwitchOneChannel,
            SwitchLiveOneChannel,
            SwitchLiveTwoChannels,
            AqaraSwitchOneChannel,
            AqaraSwitchTwoChannels,
            D1WallSwitchTriple,
            D1WallSwitchTripleNN,
            Plug,
            ThermostatS2,
            AqaraWallOutletV1,
            AqaraRelayTwoChannels,
            AqaraWallOutlet,
            SensorHT,
            AqaraHT,
        )

        # from https://github.com/aholstenson/miio/issues/26
        device_type_mapping = {
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
        self._devices = {}

        # Skip the models which do not support getting the device list
        if self.model == GATEWAY_MODEL_EU:
            _LOGGER.warning(
                "Gateway model '%s' does not (yet) support getting the device list",
                self.model,
            )
            return self._devices

        devices_raw = self.get_prop("device_list")

        for x in range(0, len(devices_raw), 5):
            # Extract discovered information
            dev_info = SubDeviceInfo(*devices_raw[x : x + 5])

            # Construct DeviceType
            try:
                device_type = DeviceType(dev_info.type_id)
            except ValueError:
                _LOGGER.warning(
                    "Unknown subdevice type %s discovered, "
                    "of Xiaomi gateway with ip: %s",
                    dev_info,
                    self.ip,
                )
                device_type = DeviceType(-1)

            # Obtain the correct subdevice class, ignoring the gateway itself
            subdevice_cls = device_type_mapping.get(device_type)
            if subdevice_cls is None and device_type != DeviceType.Gateway:
                subdevice_cls = SubDevice
                _LOGGER.info(
                    "Gateway device type '%s' "
                    "does not have device specific methods defined, "
                    "only basic default methods will be available",
                    device_type.name,
                )

            # Initialize and save the subdevice, ignoring the gateway itself
            if device_type != DeviceType.Gateway:
                self._devices[dev_info.sid] = subdevice_cls(self, dev_info)
                if self._devices[dev_info.sid].status == {}:
                    _LOGGER.info(
                        "Discovered subdevice type '%s', has no device specific properties defined, "
                        "this device has not been fully implemented yet (model: %s, name: %s).",
                        device_type.name,
                        self._devices[dev_info.sid].model,
                        self._devices[dev_info.sid].name,
                    )

        return self._devices

    @command(click.argument("property"))
    def get_prop(self, property):
        """Get the value of a property for given sid."""
        return self.send("get_device_prop", ["lumi.0", property])

    @command(click.argument("properties", nargs=-1))
    def get_prop_exp(self, properties):
        """Get the value of a bunch of properties for given sid."""
        return self.send("get_device_prop_exp", [["lumi.0"] + list(properties)])

    @command(click.argument("property"), click.argument("value"))
    def set_prop(self, property, value):
        """Set the device property."""
        return self.send("set_device_prop", {"sid": "lumi.0", property: value})

    @command()
    def clock(self):
        """Alarm clock"""
        # payload of clock volume ("get_clock_volume")
        # already in get_clock response
        return self.send("get_clock")

    # Developer key
    @command()
    def get_developer_key(self):
        """Return the developer API key."""
        return self.send("get_lumi_dpf_aes_key")[0]

    @command(click.argument("key"))
    def set_developer_key(self, key):
        """Set the developer API key."""
        if len(key) != 16:
            click.echo("Key must be of length 16, was %s" % len(key))

        return self.send("set_lumi_dpf_aes_key", [key])

    @command()
    def enable_telnet(self):
        """Enable root telnet acces to the operating system, use login "admin" or "app", no password."""
        try:
            return self.send("enable_telnet_service")
        except DeviceError:
            _LOGGER.error(
                "Gateway model '%s' does not (yet) support enabling the telnet interface",
                self.model,
            )
            return None

    @command()
    def timezone(self):
        """Get current timezone."""
        return self.get_prop("tzone_sec")

    @command()
    def get_illumination(self):
        """Get illumination. In lux?"""
        return self.send("get_illumination").pop()
