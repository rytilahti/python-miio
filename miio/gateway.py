"""Xiaomi Aqara Gateway implementation using Miio protecol."""

import logging
from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional, Tuple

import attr
import click

from .click_common import EnumType, command, format_output
from .device import Device
from .exceptions import DeviceError, DeviceException
from .utils import brightness_and_color_to_int, int_to_brightness, int_to_rgb

_LOGGER = logging.getLogger(__name__)

GATEWAY_MODEL_CHINA = "lumi.gateway.v3"
GATEWAY_MODEL_EU = "lumi.gateway.mieu01"
GATEWAY_MODEL_ZIG3 = "lumi.gateway.mgl03"
GATEWAY_MODEL_AQARA = "lumi.gateway.aqhm01"
GATEWAY_MODEL_AC_V1 = "lumi.acpartner.v1"
GATEWAY_MODEL_AC_V2 = "lumi.acpartner.v2"
GATEWAY_MODEL_AC_V3 = "lumi.acpartner.v3"

color_map = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "aqua": (0, 255, 255),
    "olive": (128, 128, 0),
    "purple": (128, 0, 128),
}


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


@attr.s(auto_attribs=True)
class SubDeviceInfo:
    """SubDevice discovery info."""

    sid: str
    type_id: int
    unknown: int
    unknown2: int
    fw_ver: int


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
        self._alarm = GatewayAlarm(parent=self)
        self._radio = GatewayRadio(parent=self)
        self._zigbee = GatewayZigbee(parent=self)
        self._light = GatewayLight(parent=self)
        self._devices = {}
        self._info = None

    @property
    def alarm(self) -> "GatewayAlarm":
        """Return alarm control interface."""
        # example: gateway.alarm.on()
        return self._alarm

    @property
    def radio(self) -> "GatewayRadio":
        """Return radio control interface."""
        return self._radio

    @property
    def zigbee(self) -> "GatewayZigbee":
        """Return zigbee control interface."""
        return self._zigbee

    @property
    def light(self) -> "GatewayLight":
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
        try:
            return self.send("get_illumination").pop()
        except Exception as ex:
            raise GatewayException(
                "Got an exception while getting gateway illumination"
            ) from ex


class GatewayDevice(Device):
    """
    GatewayDevice class
    Specifies the init method for all gateway device functionalities.
    """

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        parent: Gateway = None,
    ) -> None:
        if parent is not None:
            self._gateway = parent
        else:
            self._gateway = Device(ip, token, start_id, debug, lazy_discover)
            _LOGGER.debug(
                "Creating new device instance, only use this for cli interface"
            )


class GatewayAlarm(GatewayDevice):
    """Class representing the Xiaomi Gateway Alarm."""

    @command(default_output=format_output("[alarm_status]"))
    def status(self) -> str:
        """Return the alarm status from the device."""
        # Response: 'on', 'off', 'oning'
        return self._gateway.send("get_arming").pop()

    @command(default_output=format_output("Turning alarm on"))
    def on(self):
        """Turn alarm on."""
        return self._gateway.send("set_arming", ["on"])

    @command(default_output=format_output("Turning alarm off"))
    def off(self):
        """Turn alarm off."""
        return self._gateway.send("set_arming", ["off"])

    @command()
    def arming_time(self) -> int:
        """
        Return time in seconds the alarm stays 'oning'
        before transitioning to 'on'
        """
        # Response: 5, 15, 30, 60
        return self._gateway.send("get_arm_wait_time").pop()

    @command(click.argument("seconds"))
    def set_arming_time(self, seconds):
        """Set time the alarm stays at 'oning' before transitioning to 'on'."""
        return self._gateway.send("set_arm_wait_time", [seconds])

    @command()
    def triggering_time(self) -> int:
        """Return the time in seconds the alarm is going off when triggered."""
        # Response: 30, 60, etc.
        return self._gateway.get_prop("alarm_time_len").pop()

    @command(click.argument("seconds"))
    def set_triggering_time(self, seconds):
        """Set the time in seconds the alarm is going off when triggered."""
        return self._gateway.set_prop("alarm_time_len", seconds)

    @command()
    def triggering_light(self) -> int:
        """
        Return the time the gateway light blinks
        when the alarm is triggerd
        """
        # Response: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.get_prop("en_alarm_light").pop()

    @command(click.argument("seconds"))
    def set_triggering_light(self, seconds):
        """Set the time the gateway light blinks when the alarm is triggerd."""
        # values: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.set_prop("en_alarm_light", seconds)

    @command()
    def triggering_volume(self) -> int:
        """Return the volume level at which alarms go off [0-100]."""
        return self._gateway.send("get_alarming_volume").pop()

    @command(click.argument("volume"))
    def set_triggering_volume(self, volume):
        """Set the volume level at which alarms go off [0-100]."""
        return self._gateway.send("set_alarming_volume", [volume])

    @command()
    def last_status_change_time(self) -> datetime:
        """
        Return the last time the alarm changed status.
        """
        return datetime.fromtimestamp(self._gateway.send("get_arming_time").pop())


class GatewayZigbee(GatewayDevice):
    """Zigbee controls."""

    @command()
    def get_zigbee_version(self):
        """timeouts on device."""
        return self._gateway.send("get_zigbee_device_version")

    @command()
    def get_zigbee_channel(self):
        """Return currently used zigbee channel."""
        return self._gateway.send("get_zigbee_channel")[0]

    @command(click.argument("channel"))
    def set_zigbee_channel(self, channel):
        """Set zigbee channel."""
        return self._gateway.send("set_zigbee_channel", [channel])

    @command(click.argument("timeout", type=int))
    def zigbee_pair(self, timeout):
        """Start pairing, use 0 to disable."""
        return self._gateway.send("start_zigbee_join", [timeout])

    def send_to_zigbee(self):
        """How does this differ from writing? Unknown."""
        raise NotImplementedError()
        return self._gateway.send("send_to_zigbee")

    def read_zigbee_eep(self):
        """Read eeprom?"""
        raise NotImplementedError()
        return self._gateway.send("read_zig_eep", [0])  # 'ok'

    def read_zigbee_attribute(self):
        """Read zigbee data?"""
        raise NotImplementedError()
        return self._gateway.send("read_zigbee_attribute", [0x0000, 0x0080])

    def write_zigbee_attribute(self):
        """Unknown parameters."""
        raise NotImplementedError()
        return self._gateway.send("write_zigbee_attribute")

    @command()
    def zigbee_unpair_all(self):
        """Unpair all devices."""
        return self._gateway.send("remove_all_device")

    def zigbee_unpair(self, sid):
        """Unpair a device."""
        # get a device obj an call dev.unpair()
        raise NotImplementedError()


class GatewayRadio(GatewayDevice):
    """Radio controls for the gateway."""

    @command()
    def get_radio_info(self):
        """Radio play info."""
        return self._gateway.send("get_prop_fm")

    @command(click.argument("volume"))
    def set_radio_volume(self, volume):
        """Set radio volume."""
        return self._gateway.send("set_fm_volume", [volume])

    def play_music_new(self):
        """Unknown."""
        # {'from': '4', 'id': 9514,
        #  'method': 'set_default_music', 'params': [2, '21']}
        # {'from': '4', 'id': 9515,
        #  'method': 'play_music_new', 'params': ['21', 0]}
        raise NotImplementedError()

    def play_specify_fm(self):
        """play specific stream?"""
        raise NotImplementedError()
        # {"from": "4", "id": 65055, "method": "play_specify_fm",
        # "params": {"id": 764, "type": 0,
        # "url": "http://live.xmcdn.com/live/764/64.m3u8"}}
        return self._gateway.send("play_specify_fm")

    def play_fm(self):
        """radio on/off?"""
        raise NotImplementedError()
        # play_fm","params":["off"]}
        return self._gateway.send("play_fm")

    def volume_ctrl_fm(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("volume_ctrl_fm")

    def get_channels(self):
        """Unknown."""
        raise NotImplementedError()
        # "method": "get_channels", "params": {"start": 0}}
        return self._gateway.send("get_channels")

    def add_channels(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("add_channels")

    def remove_channels(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("remove_channels")

    def get_default_music(self):
        """seems to timeout (w/o internet)."""
        # params [0,1,2]
        raise NotImplementedError()
        return self._gateway.send("get_default_music")

    @command()
    def get_music_info(self):
        """Unknown."""
        info = self._gateway.send("get_music_info")
        click.echo("info: %s" % info)
        free_space = self._gateway.send("get_music_free_space")
        click.echo("free space: %s" % free_space)

    @command()
    def get_mute(self):
        """mute of what?"""
        return self._gateway.send("get_mute")

    def download_music(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("download_music")

    def delete_music(self):
        """delete music."""
        raise NotImplementedError()
        return self._gateway.send("delete_music")

    def download_user_music(self):
        """Unknown."""
        raise NotImplementedError()
        return self._gateway.send("download_user_music")

    def get_download_progress(self):
        """progress for music downloads or updates?"""
        # returns [':0']
        raise NotImplementedError()
        return self._gateway.send("get_download_progress")

    @command()
    def set_sound_playing(self):
        """stop playing?"""
        return self._gateway.send("set_sound_playing", ["off"])

    def set_default_music(self):
        """Unknown."""
        raise NotImplementedError()
        # method":"set_default_music","params":[0,"2"]}


class GatewayLight(GatewayDevice):
    """
    Light controls for the gateway.

    The gateway LEDs can be controlled using 'rgb' or 'night_light' methods.
    The 'night_light' methods control the same light as the 'rgb' methods, but has a separate memory for brightness and color.
    Changing the 'rgb' light does not affect the stored state of the 'night_light', while changing the 'night_light' does effect the state of the 'rgb' light.
    """

    @command()
    def rgb_status(self):
        """
        Get current status of the light.
        Always represents the current status of the light as opposed to 'night_light_status'.

        Example:
           {"is_on": false, "brightness": 0, "rgb": (0, 0, 0)}
        """
        # Returns {"is_on": false, "brightness": 0, "rgb": (0, 0, 0)} when light is off
        state_int = self._gateway.send("get_rgb").pop()
        brightness = int_to_brightness(state_int)
        rgb = int_to_rgb(state_int)
        is_on = brightness > 0

        return {"is_on": is_on, "brightness": brightness, "rgb": rgb}

    @command()
    def night_light_status(self):
        """
        Get status of the night light.
        This command only gives the correct status of the LEDs if the last command was a 'night_light' command and not a 'rgb' light command, otherwise it gives the stored values of the 'night_light'.

        Example:
           {"is_on": false, "brightness": 0, "rgb": (0, 0, 0)}
        """
        state_int = self._gateway.send("get_night_light_rgb").pop()
        brightness = int_to_brightness(state_int)
        rgb = int_to_rgb(state_int)
        is_on = brightness > 0

        return {"is_on": is_on, "brightness": brightness, "rgb": rgb}

    @command(
        click.argument("brightness", type=int),
        click.argument("rgb", type=(int, int, int)),
    )
    def set_rgb(self, brightness: int, rgb: Tuple[int, int, int]):
        """Set gateway light using brightness and rgb tuple."""
        brightness_and_color = brightness_and_color_to_int(brightness, rgb)

        return self._gateway.send("set_rgb", [brightness_and_color])

    @command(
        click.argument("brightness", type=int),
        click.argument("rgb", type=(int, int, int)),
    )
    def set_night_light(self, brightness: int, rgb: Tuple[int, int, int]):
        """Set gateway night light using brightness and rgb tuple."""
        brightness_and_color = brightness_and_color_to_int(brightness, rgb)

        return self._gateway.send("set_night_light_rgb", [brightness_and_color])

    @command(click.argument("brightness", type=int))
    def set_rgb_brightness(self, brightness: int):
        """Set gateway light brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = self.rgb_status()["rgb"]

        return self.set_rgb(brightness, current_color)

    @command(click.argument("brightness", type=int))
    def set_night_light_brightness(self, brightness: int):
        """Set night light brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = self.night_light_status()["rgb"]

        return self.set_night_light(brightness, current_color)

    @command(click.argument("color_name", type=str))
    def set_rgb_color(self, color_name: str):
        """Set gateway light color using color name ('color_map' variable in the source holds the valid values)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = self.rgb_status()["brightness"]

        return self.set_rgb(current_brightness, color_map[color_name])

    @command(click.argument("color_name", type=str))
    def set_night_light_color(self, color_name: str):
        """Set night light color using color name ('color_map' variable in the source holds the valid values)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = self.night_light_status()["brightness"]

        return self.set_night_light(current_brightness, color_map[color_name])

    @command(
        click.argument("color_name", type=str),
        click.argument("brightness", type=int),
    )
    def set_rgb_using_name(self, color_name: str, brightness: int):
        """Set gateway light color (using color name, 'color_map' variable in the source holds the valid values) and brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )

        return self.set_rgb(brightness, color_map[color_name])

    @command(
        click.argument("color_name", type=str),
        click.argument("brightness", type=int),
    )
    def set_night_light_using_name(self, color_name: str, brightness: int):
        """Set night light color (using color name, 'color_map' variable in the source holds the valid values) and brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )

        return self.set_night_light(brightness, color_map[color_name])


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

    def __init__(
        self,
        gw: Gateway = None,
        dev_info: SubDeviceInfo = None,
    ) -> None:
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
        return "<Subdevice %s: %s, model: %s, zigbee: %s, fw: %s, bat: %s, vol: %s, props: %s>" % (
            self.device_type,
            self.sid,
            self.model,
            self.zigbee_model,
            self.firmware_version,
            self.get_battery(),
            self.get_voltage(),
            self.status,
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
                "Gateway model '%s' does not (yet) support get_battery",
                self._gw.model,
            )
        return self._battery

    @command()
    def get_voltage(self):
        """Update the battery voltage, if available."""
        if self._gw.model == GATEWAY_MODEL_EU:
            self._voltage = self.get_property("voltage").pop() / 1000
        else:
            _LOGGER.info(
                "Gateway model '%s' does not (yet) support get_voltage",
                self._gw.model,
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


class Switch(SubDevice):
    """Subdevice Switch specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_switch"
    _model = "WXKG01LM"
    _name = "Button"


class Motion(SubDevice):
    """Subdevice Motion specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_motion"
    _model = "RTCGQ01LM"
    _name = "Motion sensor"


class Magnet(SubDevice):
    """Subdevice Magnet specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_magnet"
    _model = "MCCGQ01LM"
    _name = "Door sensor"


class SwitchTwoChannels(SubDevice):
    """Subdevice SwitchTwoChannels specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_neutral2"
    _model = "QBKG03LM"
    _name = "Wall switch double no neutral"


class Cube(SubDevice):
    """Subdevice Cube specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_cube.v1"
    _model = "MFKZQ01LM"
    _name = "Cube"


class SwitchOneChannel(SubDevice):
    """Subdevice SwitchOneChannel specific properties and methods."""

    properties = ["neutral_0"]
    _zigbee_model = "lumi.ctrl_neutral1.v1"
    _model = "QBKG04LM"
    _name = "Wall switch no neutral"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]

    @command()
    def toggle(self):
        """Toggle Switch One Channel."""
        return self.send_arg("toggle_ctrl_neutral", ["channel_0", "toggle"]).pop()

    @command()
    def on(self):
        """Turn on Switch One Channel."""
        return self.send_arg("toggle_ctrl_neutral", ["channel_0", "on"]).pop()

    @command()
    def off(self):
        """Turn off Switch One Channel."""
        return self.send_arg("toggle_ctrl_neutral", ["channel_0", "off"]).pop()


class SensorHT(SubDevice):
    """Subdevice SensorHT specific properties and methods."""

    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity"]
    _zigbee_model = "lumi.sensor_ht"
    _model = "WSDCGQ01LM"
    _name = "Weather sensor"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        temperature: int = None  # in degrees celsius
        humidity: int = None  # in %

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        try:
            self._props.temperature = values[0] / 100
            self._props.humidity = values[1] / 100
        except Exception as ex:
            raise GatewayException(
                "One or more unexpected results while "
                "fetching properties %s: %s" % (self.properties, values)
            ) from ex


class Plug(SubDevice):
    """Subdevice Plug specific properties and methods."""

    accessor = "get_prop_plug"
    properties = ["neutral_0", "load_power"]
    _zigbee_model = "lumi.plug"
    _model = "ZNCZ02LM"
    _name = "Plug"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in Watt

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]
        self._props.load_power = values[1]

    @command()
    def toggle(self):
        """Toggle Plug."""
        return self.send_arg("toggle_plug", ["channel_0", "toggle"]).pop()

    @command()
    def on(self):
        """Turn on Plug."""
        return self.send_arg("toggle_plug", ["channel_0", "on"]).pop()

    @command()
    def off(self):
        """Turn off Plug."""
        return self.send_arg("toggle_plug", ["channel_0", "off"]).pop()


class RemoteSwitchDoubleV1(SubDevice):
    """Subdevice RemoteSwitchDoubleV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_86sw2.v1"
    _model = "WXKG02LM 2016"
    _name = "Remote switch double"


class CurtainV1(SubDevice):
    """Subdevice CurtainV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.curtain"
    _model = "ZNCLDJ11LM"
    _name = "Curtain"


class RemoteSwitchSingleV1(SubDevice):
    """Subdevice RemoteSwitchSingleV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_86sw1.v1"
    _model = "WXKG03LM 2016"
    _name = "Remote switch single"


class SensorSmoke(SubDevice):
    """Subdevice SensorSmoke specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_smoke"
    _model = "JTYJ-GD-01LM/BW"
    _name = "Honeywell smoke detector"


class AqaraWallOutletV1(SubDevice):
    """Subdevice AqaraWallOutletV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_86plug.v1"
    _model = "QBCZ11LM"
    _name = "Wall outlet"


class SensorNatgas(SubDevice):
    """Subdevice SensorNatgas specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_natgas"
    _model = "JTQJ-BF-01LM/BW"
    _name = "Honeywell natural gas detector"


class AqaraHT(SubDevice):
    """Subdevice AqaraHT specific properties and methods."""

    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity", "pressure"]
    _zigbee_model = "lumi.weather.v1"
    _model = "WSDCGQ11LM"
    _name = "Weather sensor"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        temperature: int = None  # in degrees celsius
        humidity: int = None  # in %
        pressure: int = None  # in hPa

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        try:
            self._props.temperature = values[0] / 100
            self._props.humidity = values[1] / 100
            self._props.pressure = values[2] / 100
        except Exception as ex:
            raise GatewayException(
                "One or more unexpected results while "
                "fetching properties %s: %s" % (self.properties, values)
            ) from ex


class SwitchLiveOneChannel(SubDevice):
    """Subdevice SwitchLiveOneChannel specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_ln1"
    _model = "QBKG11LM"
    _name = "Wall switch single"


class SwitchLiveTwoChannels(SubDevice):
    """Subdevice SwitchLiveTwoChannels specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.ctrl_ln2"
    _model = "QBKG12LM"
    _name = "Wall switch double"


class AqaraSwitch(SubDevice):
    """Subdevice AqaraSwitch specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_switch.aq2"
    _model = "WXKG11LM 2015"
    _name = "Button"


class AqaraMotion(SubDevice):
    """Subdevice AqaraMotion specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_motion.aq2"
    _model = "RTCGQ11LM"
    _name = "Motion sensor"


class AqaraMagnet(SubDevice):
    """Subdevice AqaraMagnet specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_magnet.aq2"
    _model = "MCCGQ11LM"
    _name = "Door sensor"


class AqaraRelayTwoChannels(SubDevice):
    """Subdevice AqaraRelayTwoChannels specific properties and methods."""

    properties = ["load_power", "channel_0", "channel_1"]
    _zigbee_model = "lumi.relay.c2acn01"
    _model = "LLKZMK11LM"
    _name = "Relay"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in ?unit?

    class AqaraRelayToggleValue(Enum):
        """Options to control the relay."""

        toggle = "toggle"
        on = "on"
        off = "off"

    class AqaraRelayChannel(Enum):
        """Options to select wich relay to control."""

        first = "channel_0"
        second = "channel_1"

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.load_power = values[0]
        self._props.status_ch0 = values[1]
        self._props.status_ch1 = values[2]

    @command(
        click.argument("channel", type=EnumType(AqaraRelayChannel)),
        click.argument("value", type=EnumType(AqaraRelayToggleValue)),
    )
    def toggle(self, channel, value):
        """Toggle Aqara Wireless Relay 2ch."""
        return self.send_arg("toggle_ctrl_neutral", [channel.value, value.value]).pop()


class AqaraWaterLeak(SubDevice):
    """Subdevice AqaraWaterLeak specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_wleak.aq1"
    _model = "SJCGQ11LM"
    _name = "Water leak sensor"


class AqaraVibration(SubDevice):
    """Subdevice AqaraVibration specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.vibration.aq1"
    _model = "DJT11LM"
    _name = "Vibration sensor"


class DoorLockS1(SubDevice):
    """Subdevice DoorLockS1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.aq1"
    _model = "ZNMS11LM"
    _name = "Door lock S1"


class AqaraSquareButtonV3(SubDevice):
    """Subdevice AqaraSquareButtonV3 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_switch.aq3"
    _model = "WXKG12LM"
    _name = "Button"


class AqaraSwitchOneChannel(SubDevice):
    """Subdevice AqaraSwitchOneChannel specific properties and methods."""

    properties = ["neutral_0", "load_power"]
    _zigbee_model = "lumi.ctrl_ln1.aq1"
    _model = "QBKG11LM"
    _name = "Wall switch single"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in ?unit?

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]
        self._props.load_power = values[1]


class AqaraSwitchTwoChannels(SubDevice):
    """Subdevice AqaraSwitchTwoChannels specific properties and methods."""

    properties = ["neutral_0", "neutral_1", "load_power"]
    _zigbee_model = "lumi.ctrl_ln2.aq1"
    _model = "QBKG12LM"
    _name = "Wall switch double"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status_ch0: str = None  # 'on' / 'off'
        status_ch1: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in ?unit?

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status_ch0 = values[0]
        self._props.status_ch1 = values[1]
        self._props.load_power = values[2]


class AqaraWallOutlet(SubDevice):
    """Subdevice AqaraWallOutlet specific properties and methods."""

    properties = ["channel_0", "load_power"]
    _zigbee_model = "lumi.ctrl_86plug.aq1"
    _model = "QBCZ11LM"
    _name = "Wall outlet"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        load_power: int = None  # power consumption in Watt

    @command()
    def update(self):
        """Update all device properties."""
        values = self.get_property_exp(self.properties)
        self._props.status = values[0]
        self._props.load_power = values[1]

    @command()
    def toggle(self):
        """Toggle Aqara Wall Outlet."""
        return self.send_arg("toggle_plug", ["channel_0", "toggle"]).pop()

    @command()
    def on(self):
        """Turn on Aqara Wall Outlet."""
        return self.send_arg("toggle_plug", ["channel_0", "on"]).pop()

    @command()
    def off(self):
        """Turn off Aqara Wall Outlet."""
        return self.send_arg("toggle_plug", ["channel_0", "off"]).pop()


class AqaraSmartBulbE27(SubDevice):
    """Subdevice AqaraSmartBulbE27 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.light.aqcn02"
    _model = "ZNLDP12LM"
    _name = "Smart bulb E27"

    @attr.s(auto_attribs=True)
    class props:
        """Device specific properties."""

        status: str = None  # 'on' / 'off'
        brightness: int = None  # in %
        color_temp: int = None  # cct value from _ctt_min to _ctt_max
        cct_min: int = 153
        cct_max: int = 500

    @command()
    def update(self):
        """Update all device properties."""
        self._props.brightness = self.send("get_bright").pop()
        self._props.color_temp = self.send("get_ct").pop()
        if self._props.brightness > 0 and self._props.brightness <= 100:
            self._props.status = "on"
        else:
            self._props.status = "off"

    @command()
    def on(self):
        """Turn bulb on."""
        return self.send_arg("set_power", ["on"]).pop()

    @command()
    def off(self):
        """Turn bulb off."""
        return self.send_arg("set_power", ["off"]).pop()

    @command(click.argument("ctt", type=int))
    def set_color_temp(self, ctt):
        """Set the color temperature of the bulb ctt_min-ctt_max."""
        return self.send_arg("set_ct", [ctt]).pop()

    @command(click.argument("brightness", type=int))
    def set_brightness(self, brightness):
        """Set the brightness of the bulb 1-100."""
        return self.send_arg("set_bright", [brightness]).pop()


class CubeV2(SubDevice):
    """Subdevice CubeV2 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_cube.aqgl01"
    _model = "MFKZQ01LM"
    _name = "Cube"


class LockS2(SubDevice):
    """Subdevice LockS2 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.acn02"
    _model = "ZNMS12LM"
    _name = "Door lock S2"


class Curtain(SubDevice):
    """Subdevice Curtain specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.curtain.aq2"
    _model = "ZNGZDJ11LM"
    _name = "Curtain"


class CurtainB1(SubDevice):
    """Subdevice CurtainB1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.curtain.hagl04"
    _model = "ZNCLDJ12LM"
    _name = "Curtain B1"


class LockV1(SubDevice):
    """Subdevice LockV1 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.v1"
    _model = "A6121"
    _name = "Vima cylinder lock"


class IkeaBulb82(SubDevice):
    """Subdevice IkeaBulb82 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1545g12"
    _model = "LED1545G12"
    _name = "Ikea smart bulb E27 white"


class IkeaBulb83(SubDevice):
    """Subdevice IkeaBulb83 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1546g12"
    _model = "LED1546G12"
    _name = "Ikea smart bulb E27 white"


class IkeaBulb84(SubDevice):
    """Subdevice IkeaBulb84 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1536g5"
    _model = "LED1536G5"
    _name = "Ikea smart bulb E12 white"


class IkeaBulb85(SubDevice):
    """Subdevice IkeaBulb85 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1537r6"
    _model = "LED1537R6"
    _name = "Ikea smart bulb GU10 white"


class IkeaBulb86(SubDevice):
    """Subdevice IkeaBulb86 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1623g12"
    _model = "LED1623G12"
    _name = "Ikea smart bulb E27 white"


class IkeaBulb87(SubDevice):
    """Subdevice IkeaBulb87 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1650r5"
    _model = "LED1650R5"
    _name = "Ikea smart bulb GU10 white"


class IkeaBulb88(SubDevice):
    """Subdevice IkeaBulb88 specific properties and methods."""

    properties = []
    _zigbee_model = "ikea.light.led1649c5"
    _model = "LED1649C5"
    _name = "Ikea smart bulb E12 white"


class AqaraSquareButton(SubDevice):
    """Subdevice AqaraSquareButton specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.remote.b1acn01"
    _model = "WXKG11LM 2018"
    _name = "Button"


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


class LockS2Pro(SubDevice):
    """Subdevice LockS2Pro specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.lock.acn03"
    _model = "ZNMS13LM"
    _name = "Door lock S2 pro"


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


class D1WallSwitchTriple(SubDevice):
    """Subdevice D1WallSwitchTriple specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.switch.n3acn3"
    _model = "QBKG26LM"
    _name = "D1 wall switch triple"


class D1WallSwitchTripleNN(SubDevice):
    """Subdevice D1WallSwitchTripleNN specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.switch.l3acn3"
    _model = "QBKG25LM"
    _name = "D1 wall switch triple no neutral"


class ThermostatS2(SubDevice):
    """Subdevice ThermostatS2 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.airrtc.tcpecn02"
    _model = "KTWKQ03ES"
    _name = "Thermostat S2"
