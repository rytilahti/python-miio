import logging
from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional
from functools import reduce

import ifaddr
import click

from .click_common import EnumType, command, format_output
from .device import Device
from .utils import brightness_and_color_to_int, int_to_brightness, int_to_rgb
from .gateway_scripts import tokens, build_move, build_rotate

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


def ipv4_nonloop_ips():
    def flatten(a, b):
        a.extend(b)
        return a

    return list(
        filter(
            lambda ip: isinstance(ip, str) and not ip.startswith("127"),
            map(
                lambda ip: ip.ip,
                reduce(
                    flatten, map(lambda adapter: adapter.ips, ifaddr.get_adapters()), []
                ),
            ),
        )
    )


class DeviceType(IntEnum):
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


class AqaraRelayToggleValue(Enum):
    toggle = "toggle"
    on = "on"
    off = "off"


class AqaraRelayChannel(Enum):
    first = "channel_0"
    second = "channel_1"


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
        self._alarm = GatewayAlarm(self)
        self._radio = GatewayRadio(self)
        self._zigbee = GatewayZigbee(self)
        self._light = GatewayLight(self)

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

    @command()
    def devices(self):
        """Return list of devices."""
        # from https://github.com/aholstenson/miio/issues/26
        devices_raw = self.send("get_device_prop", ["lumi.0", "device_list"])
        devices = [
            SubDevice(self, *devices_raw[x : x + 5])  # noqa: E203
            for x in range(0, len(devices_raw), 5)
        ]

        return devices

    @command(click.argument("sid"), click.argument("property"))
    def get_device_prop(self, sid, property):
        """Get the value of a property for given sid."""
        return self.send("get_device_prop", [sid, property])

    @command(click.argument("script_id"))
    def x_del(self, script_id):
        """Get the value of a property for given sid."""
        return self.send("miIO.xdel", [script_id])

    @command(click.argument("sid"))
    def install_cube_move_script(self, sid):
        """Get the value of a property for given sid."""

        addresses = ipv4_nonloop_ips()
        my_ip = addresses[0]
        _LOGGER.info("Using address %s for callbacks of %s", my_ip, addresses)
        data_tkn = tokens['data_tkn']
        source = build_move(sid, my_ip)

        return self.send(
            "send_data_frame",
            {
                "cur": 0,
                "data": source,
                "data_tkn": data_tkn,
                "total": 1,
                "type": "scene",
            },
        )

    @command(click.argument("sid"))
    def install_cube_rotate_script(self, sid):
        """Get the value of a property for given sid."""

        addresses = ipv4_nonloop_ips()
        my_ip = addresses[0]
        _LOGGER.info("Using address %s for callbacks of %s", my_ip, addresses)
        data_tkn = tokens['data_tkn']
        source = build_rotate(sid, my_ip)

        return self.send(
            "send_data_frame",
            {
                "cur": 0,
                "data": source,
                "data_tkn": data_tkn,
                "total": 1,
                "type": "scene",
            },
        )

    @command(click.argument("sid"), click.argument("properties", nargs=-1))
    def get_device_prop_exp(self, sid, properties):
        """Get the value of a bunch of properties for given sid."""
        return self.send("get_device_prop_exp", [[sid] + list(properties)])

    @command(click.argument("sid"), click.argument("property"), click.argument("value"))
    def set_device_prop(self, sid, property, value):
        """Set the device property."""
        return self.send("set_device_prop", {"sid": sid, property: value})

    @command(click.argument("id"), click.argument("url"))
    def radio_play_url(self, id, url):
        """Put url into gateway memory with id"""
        xiaomi_url = url.replace("/", "\/")
        print(xiaomi_url)
        return self.send(
            "add_channels", {"chs": [{"id": id, "url": xiaomi_url, "type": 0}]}
        )

    @command(click.argument("id"))
    def radio_select_channel(self, id):
        """Select channel"""
        return self.send("play_specify_fm", [int(id)])

    @command(click.argument("volume"))
    def radio_volume(self, volume):
        """Set radio volume"""
        return self.send("set_fm_volume", [int(volume)])

    @command()
    def radio_info(self):
        """Radio info."""
        return self.send("get_prop_fm")

    @command()
    def radio_play(self):
        """Radio play."""
        return self.send("play_fm", ["on"])

    @command()
    def radio_stop(self):
        """Radio stop."""
        return self.send("play_fm", ["off"])

    @command()
    def radio_channels(self):
        """List of channels stored on device."""
        return self.send("get_channels", {"start": 0})

    @command(
        click.argument("sid"),
        click.argument("channel", type=EnumType(AqaraRelayChannel)),
        click.argument("value", type=EnumType(AqaraRelayToggleValue)),
    )
    def relay_toggle(self, sid, channel, value):
        """Toggle Aqara Wireless Relay 2ch"""
        return self.send(
            "toggle_ctrl_neutral",
            [channel.value, value.value],
            extra_parameters={"sid": sid},
        )[0]

    @command(
        click.argument("sid"),
        click.argument("channel", type=EnumType(AqaraRelayChannel)),
    )
    def relay_get_state(self, sid, channel):
        """Get the state of Aqara Wireless Relay 2ch for given sid"""
        return self.send("get_device_prop_exp", [[sid, channel.value]])[0][0]

    @command(click.argument("sid"))
    def relay_get_load_power(self, sid):
        """Get the the load power of Aqara Wireless Relay 2ch for given sid"""
        return self.send("get_device_prop_exp", [[sid, "load_power"]])[0][0]

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
        return self.send("get_device_prop", ["lumi.0", "tzone_sec"])

    @command()
    def get_illumination(self):
        """Get illumination. In lux?"""
        return self.send("get_illumination")[0]


class GatewayAlarm(Device):
    """Class representing the Xiaomi Gateway Alarm."""

    def __init__(self, parent) -> None:
        self._device = parent

    @command(default_output=format_output("[alarm_status]"))
    def status(self) -> str:
        """Return the alarm status from the device."""
        # Response: 'on', 'off', 'oning'
        return self._device.send("get_arming").pop()

    @command(default_output=format_output("Turning alarm on"))
    def on(self):
        """Turn alarm on."""
        return self._device.send("set_arming", ["on"])

    @command(default_output=format_output("Turning alarm off"))
    def off(self):
        """Turn alarm off."""
        return self._device.send("set_arming", ["off"])

    @command()
    def arming_time(self) -> int:
        """Return time in seconds the alarm stays 'oning' before transitioning to 'on'"""
        # Response: 5, 15, 30, 60
        return self._device.send("get_arm_wait_time").pop()

    @command(click.argument("seconds"))
    def set_arming_time(self, seconds):
        """Set time the alarm stays at 'oning' before transitioning to 'on'"""
        return self._device.send("set_arm_wait_time", [seconds])

    @command()
    def triggering_time(self) -> int:
        """Return the time in seconds the alarm is going off when triggered"""
        # Response: 30, 60, etc.
        return self._device.send("get_device_prop", ["lumi.0", "alarm_time_len"]).pop()

    @command(click.argument("seconds"))
    def set_triggering_time(self, seconds):
        """Set the time in seconds the alarm is going off when triggered"""
        return self._device.send(
            "set_device_prop", {"sid": "lumi.0", "alarm_time_len": seconds}
        )

    @command()
    def triggering_light(self) -> int:
        """Return the time the gateway light blinks when the alarm is triggerd"""
        # Response: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._device.send("get_device_prop", ["lumi.0", "en_alarm_light"]).pop()

    @command(click.argument("seconds"))
    def set_triggering_light(self, seconds):
        """Set the time the gateway light blinks when the alarm is triggerd"""
        # values: 0=do not blink, 1=always blink, x>1=blink for x seconds
        return self._device.send(
            "set_device_prop", {"sid": "lumi.0", "en_alarm_light": seconds}
        )

    @command()
    def triggering_volume(self) -> int:
        """Return the volume level at which alarms go off [0-100]"""
        return self._device.send("get_alarming_volume").pop()

    @command(click.argument("volume"))
    def set_triggering_volume(self, volume):
        """Set the volume level at which alarms go off [0-100]"""
        return self._device.send("set_alarming_volume", [volume])

    @command()
    def last_status_change_time(self):
        """Return the last time the alarm changed status, type datetime.datetime"""
        return datetime.fromtimestamp(self._device.send("get_arming_time").pop())


class GatewayZigbee(Device):
    """Zigbee controls."""

    def __init__(self, parent) -> None:
        self._device = parent

    @command()
    def get_zigbee_version(self):
        """timeouts on device"""
        return self._device.send("get_zigbee_device_version")

    @command()
    def get_zigbee_channel(self):
        """Return currently used zigbee channel."""
        return self._device.send("get_zigbee_channel")[0]

    @command(click.argument("channel"))
    def set_zigbee_channel(self, channel):
        """Set zigbee channel."""
        return self._device.send("set_zigbee_channel", [channel])

    @command(click.argument("timeout", type=int))
    def zigbee_pair(self, timeout):
        """Start pairing, use 0 to disable"""
        return self._device.send("start_zigbee_join", [timeout])

    def send_to_zigbee(self):
        """How does this differ from writing? Unknown."""
        raise NotImplementedError()
        return self._device.send("send_to_zigbee")

    def read_zigbee_eep(self):
        """Read eeprom?"""
        raise NotImplementedError()
        return self._device.send("read_zig_eep", [0])  # 'ok'

    def read_zigbee_attribute(self):
        """Read zigbee data?"""
        raise NotImplementedError()
        return self._device.send("read_zigbee_attribute", [0x0000, 0x0080])

    def write_zigbee_attribute(self):
        """Unknown parameters."""
        raise NotImplementedError()
        return self._device.send("write_zigbee_attribute")

    @command()
    def zigbee_unpair_all(self):
        """Unpair all devices."""
        return self._device.send("remove_all_device")

    def zigbee_unpair(self, sid):
        """Unpair a device."""
        # get a device obj an call dev.unpair()
        raise NotImplementedError()


class GatewayRadio(Device):
    """Radio controls for the gateway."""

    def __init__(self, parent) -> None:
        self._device = parent

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
        return self._device.send("play_specify_fm")

    def get_channels(self):
        """Unknown."""
        raise NotImplementedError()
        # "method": "get_channels", "params": {"start": 0}}
        return self._device.send("get_channels")

    def add_channels(self):
        """Unknown."""
        raise NotImplementedError()
        return self._device.send("add_channels")

    def remove_channels(self):
        """Unknown."""
        raise NotImplementedError()
        return self._device.send("remove_channels")

    def get_default_music(self):
        """seems to timeout (w/o internet)"""
        # params [0,1,2]
        raise NotImplementedError()
        return self._device.send("get_default_music")

    @command()
    def get_music_info(self):
        """Unknown."""
        info = self._device.send("get_music_info")
        click.echo("info: %s" % info)
        free_space = self._device.send("get_music_free_space")
        click.echo("free space: %s" % free_space)

    @command()
    def get_mute(self):
        """mute of what?"""
        return self._device.send("get_mute")

    def download_music(self):
        """Unknown"""
        raise NotImplementedError()
        return self._device.send("download_music")

    def delete_music(self):
        """delete music"""
        raise NotImplementedError()
        return self._device.send("delete_music")

    def download_user_music(self):
        """Unknown."""
        raise NotImplementedError()
        return self._device.send("download_user_music")

    def get_download_progress(self):
        """progress for music downloads or updates?"""
        # returns [':0']
        raise NotImplementedError()
        return self._device.send("get_download_progress")

    @command()
    def set_sound_playing(self):
        """stop playing?"""
        return self._device.send("set_sound_playing", ["off"])

    def set_default_music(self):
        raise NotImplementedError()
        # method":"set_default_music","params":[0,"2"]}


class GatewayLight(Device):
    """Light controls for the gateway."""

    def __init__(self, parent) -> None:
        self._device = parent

    @command()
    def get_night_light_rgb(self):
        """Unknown."""
        # Returns 0 when light is off?"""
        # looks like this is the same as get_rgb
        # id': 65064, 'method': 'set_night_light_rgb', 'params': [419407616]}
        # {'method': 'props', 'params': {'light': 'on', 'from.light': '4,,,'}, 'id': 88457} ?!
        return self.send("get_night_light_rgb")

    @command(click.argument("color_name", type=str))
    def set_night_light_color(self, color_name):
        """Set night light color using color name (red, green, etc)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = int_to_brightness(self.send("get_night_light_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(
            current_brightness, color_map[color_name]
        )
        return self.send("set_night_light_rgb", [brightness_and_color])

    @command(click.argument("color_name", type=str))
    def set_color(self, color_name):
        """Set gateway lamp color using color name (red, green, etc)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = int_to_brightness(self.send("get_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(
            current_brightness, color_map[color_name]
        )
        return self.send("set_rgb", [brightness_and_color])

    @command(click.argument("brightness", type=int))
    def set_brightness(self, brightness):
        """Set gateway lamp brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = int_to_rgb(self.send("get_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(brightness, current_color)
        return self.send("set_rgb", [brightness_and_color])

    @command(click.argument("brightness", type=int))
    def set_night_light_brightness(self, brightness):
        """Set night light brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = int_to_rgb(self.send("get_night_light_rgb")[0])
        brightness_and_color = brightness_and_color_to_int(brightness, current_color)
        print(brightness, current_color)
        return self.send("set_night_light_rgb", [brightness_and_color])

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
        return self.send("set_rgb", [brightness_and_color])


class SubDevice:
    def __init__(self, gw, sid, type_, _, __, ___):
        self.gw = gw
        self.sid = sid
        self.type = DeviceType(type_)

    def unpair(self):
        return self.gw.send("remove_device", [self.sid])

    def battery(self):
        return self.gw.send("get_battery", [self.sid])[0]

    def get_firmware_version(self) -> Optional[int]:
        """Returns firmware version"""
        try:
            return self.gw.send("get_device_prop", [self.sid, "fw_ver"])[0]
        except Exception as ex:
            _LOGGER.debug(
                "Got an exception while fetching fw_ver: %s", ex, exc_info=True
            )
            return None

    def __repr__(self):
        return "<Subdevice %s: %s fw: %s bat: %s>" % (
            self.type,
            self.sid,
            self.get_firmware_version(),
            self.battery(),
        )


class SensorHT(SubDevice):
    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity"]


class Plug(SubDevice):
    accessor = "get_prop_plug"
    properties = ["power", "neutral_0"]
