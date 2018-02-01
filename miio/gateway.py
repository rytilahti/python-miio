import logging
import click
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from pprint import pformat as pf
from .device import Device
from .click_common import (
    DeviceGroupMeta, device_command, echo_return_status
)

_LOGGER = logging.getLogger(__name__)

from enum import IntEnum
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
    AqaraHT = 19
    SwitchLiveOneChannel = 20
    SwitchLiveTwoChannels = 21
    AqaraSwitch = 51
    AqaraMotion = 52
    AqaraMagnet = 53

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
            _LOGGER.debug("Got an exception while fetching fw_ver: %s", ex, exc_info=True)
            return None

    def __repr__(self):
        return "<Subdevice %s: %s>" % (self.type, self.sid)

class SensorHT(SubDevice):
    accessor = "get_prop_sensor_ht"
    properties = ["temperature", "humidity"]

class Plug(SubDevice):
    accessor = "get_prop_plug"
    properties = ["power", "neutral_0"]


class Gateway(Device, metaclass=DeviceGroupMeta):
    def send(self, command: str, parameters: Any=None, retry_count=3, extra_params=None):
        if parameters is None:
            parameters = []

        return super().send(command, parameters, retry_count, extra_params)

    @device_command(echo_return_status())
    def test3(self):
        return self.send("get_device_prop_exp", [["lumi.0", "alarm_time_len", "status", "tzone_sec"]])

    @device_command(echo_return_status())
    def alarm_length(self):
        """whaat?"""
        return self.send("get_device_prop", ["lumi.0", "alarm_time_len"])

        # lumi.0 "voltage"

    @device_command(echo_return_status())
    def alarm_light(self):
        """hmhm"""
        return self.send("get_device_prop", ["lumi.0", "en_alarm_light"])

    @device_command(echo_return_status())
    def gw_timezone(self):
        # lumi.0 en_nnlight
        # lumi.0 "fm_low_rate"
        return self.send("get_device_prop", ["lumi.0", "tzone_sec"])


    @device_command(echo_return_status())
    def devices(self):
        # from https://github.com/aholstenson/miio/issues/26
        devices_raw = self.send("get_device_prop", ['lumi.0', 'device_list'])
        devices = [SubDevice(*devices_raw[x:x + 5]) for x in range(0, len(devices_raw), 5)]
        for dev in devices:
            try:
                # TEMP 10000 = unavailable, humidity stays at 0 then
                print("temperature and humidity: %s" % self.send("get_prop_sensor_ht", ["temperature", "humidity"],
                                                                 extra_params={'sid': dev.sid}))
            except Exception as ex:
                pass

    @device_command(echo_return_status())
    def test(self):
        return self.send("get_prop_sensor_ht", ["battery", "voltage", "temperature", "humidity", "lqi"], extra_params={'sid': 'lumi.158d00012db273'})

    @device_command(echo_return_status())
    def get_radio_info(self):
        """Radio play info."""
        return self.send("get_prop_fm")

    @device_command(
        click.argument("sid"),
        echo_return_status())
    def get_plug_prop(self, sid):
        return self.send("get_prop_plug", ["power", "neutral_0"], extra_params={'sid': sid})
        # {"method":"props","params":{"power":"on"},
        # :{"neutral_0":"off"}
        # {"load_power":0.00,"load_voltage":234000}

    @device_command(echo_return_status())
    def get_prop_sensor_ht(self):
        """Not working on current fw. unknown"""
        return self.send("get_prop_sensor_ht")

    @device_command(
        click.argument("sid"),
        click.argument("property"),
        echo_return_status())
    def get_device_prop(self, sid, property):
        """props? returns empty array w/o params"""
        return self.send("get_device_prop", )

    @device_command(
        click.argument("length"),
        echo_return_status())
    def set_alarm_time_length(self, length):
        # is this a typo for set?
        return self.send("get_device_prop", {'alarm_time_len': length, 'sid': 'lumi.0'})

    @device_command(echo_return_status())
    def set_device_prop(self, sid, prop):
        """props? returns empty array w/o params"""
        return self.send("set_device_prop", [sid, prop])

    @device_command(echo_return_status())
    def get_device_prop_exp(self):
        """extended props? returns empty array w/o params"""
        # externalw command? doesn't seem to work for queries
        # doesn't seem to work for lumi.0 at least..
        # from https://github.com/LASER-Yi/homebridge-mi-acpartner/issues/1
        #[192.168.31.198] -> (3) {"id":4,"method":"get_device_prop_exp","params":[["lumi.158d0001148787","status","load_voltage","load_power","power_consumed"]]}
        return self.send("get_device_prop_exp")

    @device_command(echo_return_status())
    def ctrl_device_prop(self):
        """??"""
        return self.send("ctrl_device_prop")


    # Radio
    @device_command(
        click.argument("volume"),
        echo_return_status())
    def set_radio_volume(self, volume):
        """Set radio volume"""
        return self.send("set_fm_volume", [volume])

    @device_command(echo_return_status())
    def play_music_new(self):
        """no clue"""
        # {'from': '4', 'id': 9514, 'method': 'set_default_music', 'params': [2, '21']}
        # {'from': '4', 'id': 9515, 'method': 'play_music_new', 'params': ['21', 0]}

        pass

    @device_command(echo_return_status())
    def play_specify_fm(self):
        """play specific channel? parameters unknown"""
        #{"from": "4", "id": 65055, "method": "play_specify_fm",
         # "params": {"id": 764, "type": 0, "url": "http://live.xmcdn.com/live/764/64.m3u8"}}
        return self.send("play_specify_fm")

    @device_command(echo_return_status())
    def play_fm(self):
        """radio on?"""
        # play_fm","params":["off"]}
        return self.send("play_fm")

    @device_command(echo_return_status())
    def volume_ctrl_fm(self):
        """some volume control, parameters unkn"""
        return self.send("volume_ctrl_fm")

    @device_command(echo_return_status())
    def get_channels(self):
        """returns state error, internet?"""
        # "method": "get_channels", "params": {"start": 0}}
        return self.send("get_channels")

    @device_command(echo_return_status())
    def add_channels(self):
        return self.send("add_channels")

    @device_command(echo_return_status())
    def remove_channels(self):
        return self.send("remove_channels")

    # Lights

    @device_command(echo_return_status(""))
    def get_rgb(self):
        """Unknown"""
        return self.send("get_rgb")

    @device_command(echo_return_status())
    def set_rgb(self):
        """params unknown"""
        # set off
        # {'from': '4', 'id': 65222, 'method': 'set_rgb', 'params': [0]}
        return self.send("set_rgb")

    @device_command(echo_return_status())
    def get_night_light_rgb(self):
        """Returns 0 when light is off?"""
        # looks like this is the same as get_rgb
        # id': 65064, 'method': 'set_night_light_rgb', 'params': [419407616]}
        # {'method': 'props', 'params': {'light': 'on', 'from.light': '4,,,'}, 'id': 88457} ?!
        return self.send("get_night_light_rgb")

    # Arming

    @device_command(echo_return_status())
    def disarm(self):
        """Disable alarm? dis_alarm"""
        return self.send("dis_alarm") == ['ok']


    def is_armed(self):
        return self.send("get_arming") == ['on']

    def get_arm_wait_time(self):
        """Returns time before armed?"""
        return self.send("get_arm_wait_time", [])[0]

    @device_command(
        click.argument("seconds"),
        echo_return_status())
    def set_arm_wait_time(self, seconds):
        """Sets time before armed, params unknown"""
        return self.send("set_arm_wait_time", [seconds])

    def get_arming_time(self):
        """Gets time of arm?"""
        return datetime.fromtimestamp(self.send("get_arming_time")[0])

    @device_command(echo_return_status())
    def set_arming_time(self):
        """Sets time to arm?"""
        return self.send("set_arming_time")

    @device_command(echo_return_status())
    def arm(self):
        """Returns [on,off] whether being armed?"""
        click.echo("Is armed: %s" % self.is_armed())
        click.echo("Arming time: %s" % self.get_arming_time())
        click.echo("Arm wait time: %s" % self.get_arm_wait_time())


    # Alarm clock?

    @device_command(echo_return_status())
    def clock(self):
        """Alarm clock? Arming?"""
        clock = self.send("get_clock")
        click.echo("clock: %s" % clock)
        # already inside get_clock response
        # clock_vol = self.send("get_clock_volume")
        # click.echo("clock vol: %s" % clock_vol)

    @device_command(echo_return_status())
    def set_clock(self):
        return self.send("set_clock")

    @device_command(echo_return_status())
    def set_clock_volume(self):
        """alarm clock volume?"""
        return self.send("set_clock_volume")

    @device_command(echo_return_status())
    def set_alarm(self):
        # xset possible rfom local?
        # {'method': 'miIO.xdel',  'params': ['x.timer.F466716485'], 'id': 10542153, 'from': '4'}
        #  {'method': 'miIO.xset', 'params': [['x.timer.N466716485',
        # ['0 8 * * 1,2,3,4,5', ['play_alarm_clock', 'on', '20', '20']]]], 'id': 9849577, 'from': '4'}
        pass

    # volume control

    @device_command(echo_return_status())
    def volume(self):
        """All volume settings."""
        click.echo("Gateway volume: %s" % self.get_gateway_volume())
        click.echo("Alarm volume: %s" % self.get_alarm_volume())
        click.echo("Doorbell volume: %s" % self.get_doorbell_volume())

    def get_gateway_volume(self):
        """Error/whatever from gateway?"""
        return self.send("get_gateway_volume")[0]

    def get_alarm_volume(self):
        """Current alarm volume? Returns 0"""
        return self.send("get_alarming_volume")[0]

    @device_command(
        click.argument("volume"),
        echo_return_status())
    def set_alarm_volume(self, volume):
        """Sets current volume [0-100]"""
        return self.send("set_alarming_volume", [volume])


    @device_command(echo_return_status())
    def doorbell(self):
        click.echo("Volume: %s" % self.get_doorbell_volume())
        click.echo("Push notifications? %s" % self.get_doorbell_push())

    def get_doorbell_volume(self):
        """Doorbell volume"""
        return self.send("get_doorbell_volume")[0]

    @device_command(
        click.argument("volume"),
        echo_return_status())
    def set_doorbell_volume(self, volume):
        """Sets current volume [0-100]"""
        return self.send("set_doorbell_volume", [volume])

    def get_doorbell_push(self):
        """Push doorbells to mobile?"""
        return self.send("get_doorbell_push") == 'on'

    def set_doorbell_push(self):
        """Set push doorbells to mobile?"""
        return self.send("set_doorbell_push", ["on"])


    @device_command(echo_return_status())
    def get_default_music(self):
        """seems to timeout (w/o internet)"""
        # params [0,1,2]
        return self.send("get_default_music")

    @device_command(echo_return_status())
    def get_music_info(self):
        # musicinfo takes [0]
        info = self.send("get_music_info")
        click.echo("info: %s" % info)
        free_space = self.send("get_music_free_space")
        click.echo("free space: %s" % free_space)

    @device_command(echo_return_status())
    def get_mute(self):
        """mute of what?"""
        return self.send("get_mute")

    @device_command(echo_return_status())
    def download_music(self):
        """params unknown"""
        return self.send("download_music")

    @device_command(echo_return_status())
    def delete_music(self):
        """delete music"""
        return self.send("delete_music")

    @device_command(echo_return_status())
    def download_user_music(self):
        """params unknown"""
        return self.send("download_user_music")

    @device_command(echo_return_status())
    def delete_music(self):
        """delete user music"""
        return self.send("delete_user_music")

    @device_command(echo_return_status())
    def get_download_progress(self):
        """progress for music downloads or updates?"""
        # returns [':0']
        return self.send("get_download_progress")

    @device_command(echo_return_status())
    def update_neighbor_token(self):
        # 90:{"method":"update_neighbor_token",
        # "params":[{"did":"56456852",
        # "token":"146d38d8b0cf1a5cfbb9a870c886535e",
        # "ip":"192.168.100.137"}],"id":229198,"from":"4"}
        pass

    @device_command(echo_return_status())
    def set_default_sound(self):
        """params unk"""
        return self.send("set_default_sound")

    @device_command(echo_return_status())
    def set_sound_playing(self):
        """stop playing?"""
        return self.send("set_sound_playing", ['off'])

    @device_command(echo_return_status())
    def set_default_music(self):
        pass
        # method":"set_default_music","params":[0,"2"]}

    @device_command(echo_return_status())
    def corridor(self):
        """No idea what is this."""
        click.echo("Corridor light on: %s" % self.get_corridor_light_status())
        click.echo("Corridor on time: %s" % self.get_corridor_on_time())

    def get_corridor_light_status(self):
        """get_corridor_light, gateway light [on,off]?"""
        return self.send("get_corridor_light")[0] == 'on'

    @device_command(echo_return_status())
    def set_corridor_light(self):
        """set_corridor_light, no idea.."""
        return self.send("set_corridor_light", ['off'])

    def get_corridor_on_time(self):
        """time shall be kept on?"""
        return self.send("get_corridor_on_time")[0]

    @device_command(echo_return_status())
    def set_curtain_level(self):
        """there's probably a getter too?"""
        return self.send("set_curtain_level")


    # Developer key

    def get_developer_key(self):
        """Return the developer API key."""
        return self.send("get_lumi_dpf_aes_key")[0]

    def set_developer_key(self, key):
        """Set the developer API key."""
        if len(key) != 16:
            click.echo("Key must be of length 16, was %s" % len(key))

        return self.send("set_lumi_dpf_aes_key", [key])

    @device_command(
        click.argument("key", required=False),
        echo_return_status())
    def developer_key(self, key):
        if key is not None:
            return self.set_developer_key(key)
        else:
            return self.get_developer_key()


    # Zigbee commands

    @device_command(echo_return_status())
    def zigbee(self):
        click.echo("Zigbee channel: %s" % self.get_zigbee_channel())

    @device_command(echo_return_status())
    def get_zigbee_version(self):
        """timeouts on device"""
        return self.send("get_zigbee_device_version")

    @device_command(
        click.argument("channel"),
        echo_return_status())
    def set_zigbee_channel(self, channel):
        """Set zigbee channel."""
        return self.send("set_zigbee_channel", [channel])

    def get_zigbee_channel(self):
        """Return currently used zigbee channel."""
        return self.send("get_zigbee_channel")[0]

    @device_command(
        click.argument("timeout", type=int),
        echo_return_status())
    def zigbee_pair(self, timeout):
        """Start pairing, use 0 to disable"""
        return self.send("start_zigbee_join", [timeout])

    @device_command(echo_return_status())
    def send_to_zigbee(self):
        """differs from write attribute? params?"""
        return self.send("send_to_zigbee")

    @device_command(echo_return_status())
    def read_zigbee_eep(self):
        """read eeprom?"""
        return self.send("read_zig_eep", [0])  # 'ok'

    @device_command(echo_return_status())
    def read_zigbee_attribute(self):
        """read zg"""
        return self.send("read_zigbee_attribute", [0x0000, 0x0080])

    @device_command(echo_return_status())
    def write_zigbee_attribute(self):
        """unknown params"""
        return self.send("write_zigbee_attribute")

    @device_command(echo_return_status())
    def zigbee_unpair_all(self):
        """Unpair all devices."""
        return self.send("remove_all_device")

    @device_command(
        click.argument("sid"),
        echo_return_status())
    def zigbee_unpair(self, sid):
        """Unpair a device."""
        # get a device obj an call dev.unpair()
        pass

    @device_command(echo_return_status())
    def welcome(self):
        """unknown"""
        return self.send("welcome")

    @device_command(echo_return_status())
    def get_scenes(self):
        """Returns a list of rooms/Ids associated devices?"""
        # {'cur_page': 0,
        #  'fac_scene_enable': 0,
        #  'bind_num': 4,
        #  'page': [{'id': 461316256}, {'id': 461316667}, {'id': 462261531}, {'id': 462541389}],
        #  'total_page': 1}
        page = 0  # iterate over all pages
        return self.send("get_lumi_bind", ["scene", page])

    @device_command(echo_return_status())
    def list_bind(self):
        """params error w/o params, unknown"""
        return self.send("list_bind", [0])

    @device_command(echo_return_status())
    def remove_all_bind(self):
        """removes connected devices? or network?"""
        raise NotImplementedError()
        return self.send("remove_all_bind")

    @device_command(echo_return_status())
    def occupy_sensor_cfg_get(self):
        """method not found"""
        return self.send("occupy_sensor_cfg_get")

    @device_command(echo_return_status())
    def get_system_data(self):
        """doesn't seem to work w/o internet"""
        return self.send("get_sys_data")

    @device_command(echo_return_status())
    def toggle_plug(self):
        """no clue"""
        return self.send("toggle_plug")

    @device_command(echo_return_status())
    def toggle_device(self):
        """no clue"""
        return self.send("toggle_device")

    @device_command(echo_return_status())
    def get_illumination(self):
        """lux?"""
        return self.send("get_illumination")[0]
