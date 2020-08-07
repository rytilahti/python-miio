"""Xiaomi Gateway subdevice base class."""

import logging
from typing import Optional

import attr
import click

from ...click_common import command
from ..gateway import GATEWAY_MODEL_EU, Gateway, GatewayException
from . import (
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

_LOGGER = logging.getLogger(__name__)


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


@attr.s(auto_attribs=True)
class SubDeviceInfo:
    """SubDevice discovery info."""

    sid: str
    type_id: int
    unknown: int
    unknown2: int
    fw_ver: int


class SubDevice:
    """
    Base class for all subdevices of the gateway
    these devices are connected through zigbee.
    """

    _zigbee_model = "unknown"
    _model = "unknown"
    _name = "unknown"

    @attr.s(auto_attribs=True)
    class props:
        """Defines properties of the specific device."""

    def __init__(self, gw: Gateway = None, dev_info: SubDeviceInfo = None,) -> None:
        self._gw = gw
        self.sid = dev_info.sid
        self._battery = None
        self._voltage = None
        self._fw_ver = dev_info.fw_ver
        self._props = self.props()
        try:
            self.type = DeviceType(dev_info.type_id)
        except ValueError:
            self.type = DeviceType.Unknown

    def __repr__(self):
        return (
            "<Subdevice %s: %s, model: %s, zigbee: %s, fw: %s, bat: %s, vol: %s, props: %s>"
            % (
                self.device_type,
                self.sid,
                self.model,
                self.zigbee_model,
                self.firmware_version,
                self.get_battery(),
                self.get_voltage(),
                self.status,
            )
        )

    @property
    def status(self):
        """Return sub-device status as a dict containing all properties."""
        return attr.asdict(self._props)

    @property
    def device_type(self):
        """Return the device type name."""
        return self.type.name

    @property
    def name(self):
        """Return the name of the device."""
        return f"{self._name} ({self.sid})"

    @property
    def model(self):
        """Return the device model."""
        return self._model

    @property
    def zigbee_model(self):
        """Return the zigbee device model."""
        return self._zigbee_model

    @property
    def firmware_version(self):
        """Return the firmware version."""
        return self._fw_ver

    @property
    def battery(self):
        """Return the battery level in %."""
        return self._battery

    @property
    def voltage(self):
        """Return the battery voltage in V."""
        return self._voltage

    @command()
    def update(self):
        """Update the device-specific properties."""
        _LOGGER.debug(
            "Subdevice '%s' does not have a device specific update method defined",
            self.device_type,
        )

    @command()
    def send(self, command):
        """Send a command/query to the subdevice."""
        try:
            return self._gw.send(command, [self.sid])
        except Exception as ex:
            raise GatewayException(
                "Got an exception while sending command %s" % (command)
            ) from ex

    @command()
    def send_arg(self, command, arguments):
        """Send a command/query including arguments to the subdevice."""
        try:
            return self._gw.send(command, arguments, extra_parameters={"sid": self.sid})
        except Exception as ex:
            raise GatewayException(
                "Got an exception while sending "
                "command '%s' with arguments '%s'" % (command, str(arguments))
            ) from ex

    @command(click.argument("property"))
    def get_property(self, property):
        """Get the value of a property of the subdevice."""
        try:
            response = self._gw.send("get_device_prop", [self.sid, property])
        except Exception as ex:
            raise GatewayException(
                "Got an exception while fetching property %s" % (property)
            ) from ex

        if not response:
            raise GatewayException(
                "Empty response while fetching property '%s': %s" % (property, response)
            )

        return response

    @command(click.argument("properties", nargs=-1))
    def get_property_exp(self, properties):
        """Get the value of a bunch of properties of the subdevice."""
        try:
            response = self._gw.send(
                "get_device_prop_exp", [[self.sid] + list(properties)]
            ).pop()
        except Exception as ex:
            raise GatewayException(
                "Got an exception while fetching properties %s: %s" % (properties)
            ) from ex

        if len(list(properties)) != len(response):
            raise GatewayException(
                "unexpected result while fetching properties %s: %s"
                % (properties, response)
            )

        return response

    @command(click.argument("property"), click.argument("value"))
    def set_property(self, property, value):
        """Set a device property of the subdevice."""
        try:
            return self._gw.send("set_device_prop", {"sid": self.sid, property: value})
        except Exception as ex:
            raise GatewayException(
                "Got an exception while setting propertie %s to value %s"
                % (property, str(value))
            ) from ex

    @command()
    def unpair(self):
        """Unpair this device from the gateway."""
        return self.send("remove_device")

    @command()
    def get_battery(self):
        """Update the battery level, if available."""
        if self._gw.model != GATEWAY_MODEL_EU:
            self._battery = self.send("get_battery").pop()
        else:
            _LOGGER.info(
                "Gateway model '%s' does not (yet) support get_battery", self._gw.model,
            )
        return self._battery

    @command()
    def get_voltage(self):
        """Update the battery voltage, if available."""
        if self._gw.model == GATEWAY_MODEL_EU:
            self._voltage = self.get_property("voltage").pop() / 1000
        else:
            _LOGGER.info(
                "Gateway model '%s' does not (yet) support get_voltage", self._gw.model,
            )
        return self._voltage

    @command()
    def get_firmware_version(self) -> Optional[int]:
        """Returns firmware version."""
        try:
            self._fw_ver = self.get_property("fw_ver").pop()
        except Exception as ex:
            _LOGGER.info(
                "get_firmware_version failed, returning firmware version from discovery info: %s",
                ex,
            )
        return self._fw_ver
