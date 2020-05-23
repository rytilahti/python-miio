import logging
from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device
from .exceptions import DeviceException
from .utils import brightness_and_color_to_int, int_to_brightness, int_to_rgb

_LOGGER = logging.getLogger(__name__)


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
    Unknown = -1
    Gateway = 0
    Switch = 1
    Motion = 2
    Magnet = 3
    SwitchTwoChannels = 7
    Cube = 8
    SwitchOneChannel = 9
    SensorHT = 10
    Plug = 11
    SensorSmoke = 15
    AqaraHT = 19
    SwitchLiveOneChannel = 20
    SwitchLiveTwoChannels = 21
    AqaraSwitch = 51
    AqaraMotion = 52
    AqaraMagnet = 53
    AqaraRelayTwoChannels = 54
    AqaraSquareButton = 62
    RemoteSwitchSingle = 134
    RemoteSwitchDouble = 135


class Gateway(Device):
    """Main class representing the Xiaomi Gateway.

    Use the given property getters to access specific functionalities such
    as `alarm` (for alarm controls) or `light` (for lights).

    Commands whose functionality or parameters are unknown, feel free to implement!
    * toggle_device
    * toggle_plug
    * remove_all_bind
    * list_bind [0]

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
        self._devices = []

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
        """Return a list of the already discovered devices."""
        return self._devices

    @command()
    def discover_devices(self):
        """Discovers SubDevices and returns a list of the discovered devices."""
        # from https://github.com/aholstenson/miio/issues/26
        device_type_mapping = {
            "AqaraRelayTwoChannels": AqaraRelayTwoChannels,
            "Plug": AqaraPlug,
            "SensorHT": SensorHT,
            "AqaraHT": AqaraHT,
            "AqaraMagnet": AqaraMagnet,
        }
        devices_raw = self.get_gateway_prop("device_list")
        self._devices = []

        for x in range(0, len(devices_raw), 5):
            try:
                device_name = DeviceType(devices_raw[x + 1]).name
            except ValueError:
                _LOGGER.warning(
                    "Unknown subdevice type '%i': %s discovered, of Xiaomi gateway with ip: %s",
                    devices_raw[x + 1],
                    devices_raw[x],
                    self.ip,
                )
                device_name = DeviceType(-1).name

            subdevice_cls = device_type_mapping.get(device_name)
            if subdevice_cls is None and device_name != DeviceType(0).name:
                subdevice_cls = SubDevice
                _LOGGER.info(
                    "Gateway device type '%s' does not have device specific methods defined, only basic default methods will be available",
                    device_name,
                )

            if devices_raw[x] != "lumi.0":
                self._devices.append(subdevice_cls(self, *devices_raw[x : x + 5]))

        return self._devices

    @command(click.argument("property"))
    def get_gateway_prop(self, property):
        """Get the value of a property for given sid."""
        return self.send("get_device_prop", ["lumi.0", property])

    @command(click.argument("properties", nargs=-1))
    def get_gateway_prop_exp(self, properties):
        """Get the value of a bunch of properties for given sid."""
        return self.send("get_device_prop_exp", [["lumi.0"] + list(properties)])

    @command(click.argument("property"), click.argument("value"))
    def set_gateway_prop(self, property, value):
        """Set the device property."""
        return self.send("set_device_prop", {"sid": "lumi.0", property: value})

    @command()
    def clock(self):
        """Alarm clock"""
        # payload of clock volume ("get_clock_volume") already in get_clock response
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
    def timezone(self):
        """Get current timezone."""
        return self.get_gateway_prop("tzone_sec")

    @command()
    def get_illumination(self):
        """Get illumination. In lux?"""
        return self.send("get_illumination").pop()


class GatewayAlarm(Device):
    """Class representing the Xiaomi Gateway Alarm."""

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
        """Return time in seconds the alarm stays 'oning' before transitioning to 'on'"""
        # Response: 5, 15, 30, 60
        return self._gateway.send("get_arm_wait_time").pop()

    @command(click.argument("seconds"))
    def set_arming_time(self, seconds):
        """Set time the alarm stays at 'oning' before transitioning to 'on'"""
        return self._gateway.send("set_arm_wait_time", [seconds])

    @command()
    def triggering_time(self) -> int:
        """Return the time in seconds the alarm is going off when triggered"""
        # Response: 30, 60, etc.
        return self._gateway.get_gateway_prop("alarm_time_len").pop()

    @command(click.argument("seconds"))
    def set_triggering_time(self, seconds):
        """Set the time in seconds the alarm is going off when triggered"""
        return self._gateway.set_gateway_prop("alarm_time_len", seconds)

    @command()
    def triggering_light(self) -> int:
        """Return the time the gateway light blinks when the alarm is triggerd"""
        # Response: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.get_gateway_prop("en_alarm_light").pop()

    @command(click.argument("seconds"))
    def set_triggering_light(self, seconds):
        """Set the time the gateway light blinks when the alarm is triggerd"""
        # values: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._gateway.set_gateway_prop("en_alarm_light", seconds)

    @command()
    def triggering_volume(self) -> int:
        """Return the volume level at which alarms go off [0-100]"""
        return self._gateway.send("get_alarming_volume").pop()

    @command(click.argument("volume"))
    def set_triggering_volume(self, volume):
        """Set the volume level at which alarms go off [0-100]"""
        return self._gateway.send("set_alarming_volume", [volume])

    @command()
    def last_status_change_time(self):
        """Return the last time the alarm changed status, type datetime.datetime"""
        return datetime.fromtimestamp(self._gateway.send("get_arming_time").pop())


class GatewayZigbee(Device):
    """Zigbee controls."""

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

    @command()
    def get_zigbee_version(self):
        """timeouts on device"""
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
        """Start pairing, use 0 to disable"""
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


class GatewayRadio(Device):
    """Radio controls for the gateway."""

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

    @command()
    def get_radio_info(self):
        """Radio play info."""
        return self._gateway.send("get_prop_fm")

    @command(click.argument("volume"))
    def set_radio_volume(self, volume):
        """Set radio volume"""
        return self._gateway.send("set_fm_volume", [volume])

    def play_music_new(self):
        """Unknown."""
        # {'from': '4', 'id': 9514, 'method': 'set_default_music', 'params': [2, '21']}
        # {'from': '4', 'id': 9515, 'method': 'play_music_new', 'params': ['21', 0]}
        raise NotImplementedError()

    def play_specify_fm(self):
        """play specific stream?"""
        raise NotImplementedError()
        # {"from": "4", "id": 65055, "method": "play_specify_fm",
        # "params": {"id": 764, "type": 0, "url": "http://live.xmcdn.com/live/764/64.m3u8"}}
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
        """seems to timeout (w/o internet)"""
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
        """Unknown"""
        raise NotImplementedError()
        return self._gateway.send("download_music")

    def delete_music(self):
        """delete music"""
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


class GatewayLight(Device):
    """Light controls for the gateway."""

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

    @command()
    def get_night_light_rgb(self):
        """Unknown."""
        # Returns 0 when light is off?"""
        # looks like this is the same as get_rgb
        # id': 65064, 'method': 'set_night_light_rgb', 'params': [419407616]}
        # {'method': 'props', 'params': {'light': 'on', 'from.light': '4,,,'}, 'id': 88457} ?!
        return self._gateway.send("get_night_light_rgb")

    @command(click.argument("color_name", type=str))
    def set_night_light_color(self, color_name):
        """Set night light color using color name (red, green, etc)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = int_to_brightness(
            self._gateway.send("get_night_light_rgb")[0]
        )
        brightness_and_color = brightness_and_color_to_int(
            current_brightness, color_map[color_name]
        )
        return self._gateway.send("set_night_light_rgb", [brightness_and_color])

    @command(click.argument("color_name", type=str))
    def set_color(self, color_name):
        """Set gateway lamp color using color name (red, green, etc)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = int_to_brightness(self._gateway.send("get_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(
            current_brightness, color_map[color_name]
        )
        return self._gateway.send("set_rgb", [brightness_and_color])

    @command(click.argument("brightness", type=int))
    def set_brightness(self, brightness):
        """Set gateway lamp brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = int_to_rgb(self._gateway.send("get_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(brightness, current_color)
        return self._gateway.send("set_rgb", [brightness_and_color])

    @command(click.argument("brightness", type=int))
    def set_night_light_brightness(self, brightness):
        """Set night light brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = int_to_rgb(self._gateway.send("get_night_light_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(brightness, current_color)
        print(brightness, current_color)
        return self._gateway.send("set_night_light_rgb", [brightness_and_color])

    @command(
        click.argument("color_name", type=str), click.argument("brightness", type=int)
    )
    def set_light(self, color_name, brightness):
        """Set color (using color name) and brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        brightness_and_color = brightness_and_color_to_int(
            brightness, color_map[color_name]
        )
        return self._gateway.send("set_rgb", [brightness_and_color])


class SubDevice(Device):
    def __init__(
        self,
        gw: Gateway = None,
        sid: str = None,
        type: int = None,
        _: int = None,
        __: int = None,
        ___: int = None,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        if gw is not None:
            self._gw = gw
        else:
            self._gw = Device(ip, token, start_id, debug, lazy_discover)
            _LOGGER.debug(
                "Creating new device instance, only use this for cli interface"
            )

        if sid is None:
            raise Exception("sid of the subdevice needs to be specified")

        self._gw = gw
        self.sid = sid
        self._battery = None
        try:
            self.type = DeviceType(type)
        except ValueError:
            self.type = DeviceType(-1)

    def __repr__(self):
        return "<Subdevice %s: %s fw: %s bat: %s>" % (
            self.device_type,
            self.sid,
            self.get_firmware_version(),
            self.get_battery(),
        )

    @property
    def device_type(self):
        """Return the device type name."""
        return self.type.name

    @property
    def battery(self):
        """Return the battery level."""
        return self._battery

    @command()
    def subdevice_send(self, command):
        """Send a command/query to the subdevice"""
        try:
            return self._gw.send(command, [self.sid])
        except Exception as ex:
            raise GatewayException(
                    "Got an exception while sending command %s"
                    % (command)
                ) from ex
            return None

    @command()
    def subdevice_send_arg(self, command, arguments):
        """Send a command/query including arguments to the subdevice"""
        try:
            return self._gw.send(command, arguments, extra_parameters={"sid": self.sid})
        except Exception as ex:
            raise GatewayException(
                "Got an exception while sending command '%s' with arguments '%s'"
                % (command, str(arguments))
            ) from ex

    @command(click.argument("property"))
    def get_subdevice_prop(self, property):
        """Get the value of a property of the subdevice."""
        try:
            response = self._gw.send("get_device_prop", [self.sid, property])
        except Exception as ex:
            raise GatewayException(
                "Got an exception while fetching property %s" % (property)
            ) from ex

        if not response:
            raise GatewayException(
                "Empty response while fetching property %s: %s" % (property, response)
            )

        return response

    @command(click.argument("properties", nargs=-1))
    def get_subdevice_prop_exp(self, properties):
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

        for item in response:
            if not item:
                raise GatewayException(
                    "One or more empty results while fetching properties %s: %s"
                    % (properties, response)
                )

        return response

    @command(click.argument("property"), click.argument("value"))
    def set_subdevice_prop(self, property, value):
        """Set a device property of the subdevice."""
        try:
            return self._gw.send("set_device_prop", {"sid": self.sid, property: value})
        except Exception as ex:
            raise GatewayException(
                "Got an exception while setting propertie %s to value %s: %s"
                % (property, str(value))
            ) from ex

    @command()
    def unpair(self):
        """Unpair this device from the gateway."""
        return self.subdevice_send("remove_device")

    @command()
    def get_battery(self):
        """Update the battery level and return the new value."""
        self._battery = self.subdevice_send("get_battery").pop()
        return self._battery

    @command()
    def get_firmware_version(self) -> Optional[int]:
        """Returns firmware version"""
        return self.get_subdevice_prop("fw_ver").pop()


class AqaraHT(SubDevice):
    _temperature = None
    _humidity = None
    _pressure = None

    @property
    def temperature(self):
        """Return the temperature in degrees celsius"""
        return self._temperature

    @property
    def humidity(self):
        """Return the humidity in %"""
        return self._humidity

    @property
    def pressure(self):
        """Return the pressure in hPa"""
        return self._pressure

    @command()
    def update(self):
        """Update all device properties"""
        values = self.get_subdevice_prop_exp(["temperature", "humidity", "pressure"])
        self._temperature = values[0] / 100
        self._humidity = values[1] / 100
        self._pressure = values[2] / 100


class SensorHT(SubDevice):
    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity"]
    _temperature = None
    _humidity = None

    @property
    def temperature(self):
        """Return the temperature in degrees celsius"""
        return self._temperature

    @property
    def humidity(self):
        """Return the humidity in %"""
        return self._humidity

    @command()
    def update(self):
        """Update all device properties"""
        values = self.get_subdevice_prop_exp(self.properties)
        self._temperature = values[0] / 100
        self._humidity = values[1] / 100


class AqaraMagnet(SubDevice):
    _status = None

    @property
    def status(self):
        """Returns 'open' or 'closed'"""
        return self._status

    @command()
    def update(self):
        """Update all device properties"""
        values = self.get_subdevice_prop_exp(["unkown"])
        self._status = values[0]


class AqaraPlug(SubDevice):
    accessor = "get_prop_plug"
    properties = ["power", "neutral_0"]
    _power = None
    _status = None

    @property
    def power(self):
        """Return the power consumption"""
        return self._power

    @property
    def status(self):
        """Return the status of the plug: on/off"""
        return self._status

    @command()
    def update(self):
        """Update all device properties"""
        values = self.get_subdevice_prop_exp(self.properties)
        self._power = values[0]
        self._status = values[1]


class AqaraRelayTwoChannels(SubDevice):
    _status_ch0 = None
    _status_ch1 = None
    _load_power = None

    class AqaraRelayToggleValue(Enum):
        """Options to control the relay"""
        toggle = "toggle"
        on = "on"
        off = "off"

    class AqaraRelayChannel(Enum):
        """Options to select wich relay to control"""
        first = "channel_0"
        second = "channel_1"

    @property
    def status_ch0(self):
        """Return the state of channel 0"""
        return self._status_ch0

    @property
    def status_ch1(self):
        """Return the state of channel 1"""
        return self._status_ch1

    @property
    def load_power(self):
        """Return the load power"""
        return self._load_power

    @command()
    def update(self):
        """Update all device properties"""
        values = self.get_subdevice_prop_exp(["load_power", "channel_0", "channel_1"])
        self._load_power = values[0]
        self._status_ch0 = values[1]
        self._status_ch1 = values[2]

    @command(
        click.argument("channel", type=EnumType(AqaraRelayChannel)),
        click.argument("value", type=EnumType(AqaraRelayToggleValue)),
    )
    def toggle(self, sid, channel, value):
        """Toggle Aqara Wireless Relay 2ch"""
        return self.subdevice_send_arg(
            "toggle_ctrl_neutral", [channel.value, value.value]
        ).pop()
