import logging
import click
from typing import Optional
from datetime import datetime

from .device import Device
from .click_common import command, format_output
from .utils import int_to_rgb, int_to_brightness, brightness_and_color_to_int
from enum import IntEnum

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


class Gateway(Device):
    """Main class representing the Xiaomi Gateway."""

    def __init__(self, ip: str = None, token: str = None,) -> None:
        super().__init__(ip, token)
        self._alarm = GatewayAlarm(self)

    @property
    def alarm(self):
        """Returns initialized GatewayAlarm class with all its functions."""
        # example: gateway.alarm.on()
        return self._alarm

    @command()
    def test3(self):
        return self.send(
            "get_device_prop_exp", [["lumi.0", "alarm_time_len", "status", "tzone_sec"]]
        )

    @command()
    def gw_timezone(self):
        # lumi.0 en_nnlight
        # lumi.0 "fm_low_rate"
        return self.send("get_device_prop", ["lumi.0", "tzone_sec"])

    @command()
    def devices(self):
        # from https://github.com/aholstenson/miio/issues/26
        devices_raw = self.send("get_device_prop", ["lumi.0", "device_list"])
        devices = [
            SubDevice(self, *devices_raw[x : x + 5])  # noqa: E203
            for x in range(0, len(devices_raw), 5)
        ]
        for dev in devices:
            try:
                print(dev)
                # TEMP 10000 = unavailable, humidity stays at 0 then
                print(
                    "temperature and humidity: %s"
                    % self.send(
                        "get_prop_sensor_ht",
                        ["temperature", "humidity"],
                        extra_params={"sid": dev.sid},
                    )
                )
            except Exception as ex:
                _LOGGER.error("Unable to read device properties: %s", ex, exc_info=True)
                continue

    @command()
    def test(self):
        raise Exception("just for testing purposes, sid needs to be changed.")
        return self.send(
            "get_prop_sensor_ht",
            ["battery", "voltage", "temperature", "humidity", "lqi"],
            extra_params={"sid": "lumi.158d00012db273"},
        )

    @command()
    def get_radio_info(self):
        """Radio play info."""
        return self.send("get_prop_fm")

    @command(click.argument("sid"))
    def get_plug_prop(self, sid):
        return self.send(
            "get_prop_plug", ["power", "neutral_0"], extra_params={"sid": sid}
        )
        # {"method":"props","params":{"power":"on"},
        # :{"neutral_0":"off"}
        # {"load_power":0.00,"load_voltage":234000}

    @command()
    def get_prop_sensor_ht(self):
        """Not working on current fw. unknown"""
        return self.send("get_prop_sensor_ht")

    @command(
        click.argument("sid"), click.argument("property"),
    )
    def get_device_prop(self, sid, property):
        """props? returns empty array w/o params"""
        return self.send("get_device_prop")

    @command()
    def set_device_prop(self, sid, prop, prop_val):
        """set a device property, sid="lumi.0" for the gateway"""
        return self.send("set_device_prop", {"sid": sid, prop: prop_val})

    @command()
    def get_device_prop_exp(self):
        """extended props? returns empty array w/o params"""
        # externalw command? doesn't seem to work for queries
        # doesn't seem to work for lumi.0 at least..
        # from https://github.com/LASER-Yi/homebridge-mi-acpartner/issues/1
        # [192.168.31.198] -> (3) {"id":4,"method":"get_device_prop_exp",
        # "params":[
        # ["lumi.158d0001148787",
        # "status","load_voltage","load_power","power_consumed"]]}
        return self.send("get_device_prop_exp")

    @command()
    def ctrl_device_prop(self):
        """??"""
        return self.send("ctrl_device_prop")

    # Radio
    @command(click.argument("volume"))
    def set_radio_volume(self, volume):
        """Set radio volume"""
        return self.send("set_fm_volume", [volume])

    @command()
    def play_music_new(self):
        """no clue"""
        # {'from': '4', 'id': 9514, 'method': 'set_default_music', 'params': [2, '21']}
        # {'from': '4', 'id': 9515, 'method': 'play_music_new', 'params': ['21', 0]}
        raise NotImplementedError()

    @command()
    def play_specify_fm(self):
        """play specific channel? parameters unknown"""
        # {"from": "4", "id": 65055, "method": "play_specify_fm",
        # "params": {"id": 764, "type": 0, "url": "http://live.xmcdn.com/live/764/64.m3u8"}}
        return self.send("play_specify_fm")

    @command()
    def play_fm(self):
        """radio on?"""
        # play_fm","params":["off"]}
        return self.send("play_fm")

    @command()
    def volume_ctrl_fm(self):
        """some volume control, parameters unkn"""
        return self.send("volume_ctrl_fm")

    @command()
    def get_channels(self):
        """returns state error, internet?"""
        # "method": "get_channels", "params": {"start": 0}}
        return self.send("get_channels")

    @command()
    def add_channels(self):
        return self.send("add_channels")

    @command()
    def remove_channels(self):
        return self.send("remove_channels")

    # Lights

    @command()
    def get_rgb(self):
        """Unknown"""
        return self.send("get_rgb")

    @command()
    def set_rgb(self):
        """params unknown"""
        # set off
        # {'from': '4', 'id': 65222, 'method': 'set_rgb', 'params': [0]}
        return self.send("set_rgb")

    @command()
    def get_night_light_rgb(self):
        """Returns 0 when light is off?"""
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

    # Clock
    @command()
    def clock(self):
        """Alarm clock? Arming?"""
        clock = self.send("get_clock")
        click.echo("clock: %s" % clock)
        # already inside get_clock response
        # clock_vol = self.send("get_clock_volume")
        # click.echo("clock vol: %s" % clock_vol)

    @command()
    def set_clock(self):
        return self.send("set_clock")

    @command()
    def set_clock_volume(self):
        """alarm clock volume?"""
        return self.send("set_clock_volume")

    @command()
    def set_alarm(self):
        # xset possible rfom local?
        # {'method': 'miIO.xdel',  'params': ['x.timer.F466716485'], 'id': 10542153, 'from': '4'}
        #  {'method': 'miIO.xset', 'params': [['x.timer.N466716485',
        # ['0 8 * * 1,2,3,4,5', ['play_alarm_clock', 'on', '20', '20']]]], 'id': 9849577, 'from': '4'}
        raise NotImplementedError()

    # volume control

    @command()
    def volume(self):
        """All volume settings."""
        click.echo("Gateway volume: %s" % self.get_gateway_volume())
        click.echo("Doorbell volume: %s" % self.get_doorbell_volume())

    def get_gateway_volume(self):
        """Error/whatever from gateway?"""
        return self.send("get_gateway_volume")[0]

    def set_gateway_volume(self):
        """Set gateway volume."""
        return self.send("set_gateway_volume")[0]

    @command()
    def doorbell(self):
        click.echo("Volume: %s" % self.get_doorbell_volume())
        click.echo("Push notifications? %s" % self.get_doorbell_push())

    def get_doorbell_volume(self):
        """Doorbell volume"""
        return self.send("get_doorbell_volume")[0]

    @command(click.argument("volume"))
    def set_doorbell_volume(self, volume):
        """Sets current volume [0-100]"""
        return self.send("set_doorbell_volume", [volume])

    def get_doorbell_push(self):
        """Push doorbells to mobile?"""
        return self.send("get_doorbell_push") == "on"

    def set_doorbell_push(self):
        """Set push doorbells to mobile?"""
        return self.send("set_doorbell_push", ["on"])

    @command()
    def get_default_music(self):
        """seems to timeout (w/o internet)"""
        # params [0,1,2]
        return self.send("get_default_music")

    @command()
    def get_music_info(self):
        # musicinfo takes [0]
        info = self.send("get_music_info")
        click.echo("info: %s" % info)
        free_space = self.send("get_music_free_space")
        click.echo("free space: %s" % free_space)

    @command()
    def get_mute(self):
        """mute of what?"""
        return self.send("get_mute")

    @command()
    def download_music(self):
        """params unknown"""
        return self.send("download_music")

    @command()
    def delete_music(self):
        """delete music"""
        return self.send("delete_music")

    @command()
    def download_user_music(self):
        """params unknown"""
        return self.send("download_user_music")

    @command()
    def get_download_progress(self):
        """progress for music downloads or updates?"""
        # returns [':0']
        return self.send("get_download_progress")

    @command()
    def update_neighbor_token(self):
        # 90:{"method":"update_neighbor_token",
        # "params":[{"did":"56456852",
        # "token":"146d38d8b0cf1a5cfbb9a870c886535e",
        # "ip":"192.168.100.137"}],"id":229198,"from":"4"}
        raise NotImplementedError()

    @command()
    def set_default_sound(self):
        """params unk"""
        return self.send("set_default_sound")

    @command()
    def set_sound_playing(self):
        """stop playing?"""
        return self.send("set_sound_playing", ["off"])

    @command()
    def set_default_music(self):
        raise NotImplementedError()
        # method":"set_default_music","params":[0,"2"]}

    @command()
    def corridor(self):
        """No idea what is this."""
        click.echo("Corridor light on: %s" % self.get_corridor_light_status())
        click.echo("Corridor on time: %s" % self.get_corridor_on_time())

    def get_corridor_light_status(self):
        """get_corridor_light, gateway light [on,off]?"""
        return self.send("get_corridor_light")[0] == "on"

    @command()
    def set_corridor_light(self):
        """set_corridor_light, no idea.."""
        return self.send("set_corridor_light", ["off"])

    def get_corridor_on_time(self):
        """time shall be kept on?"""
        return self.send("get_corridor_on_time")[0]

    @command()
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

    @command(click.argument("key", required=False))
    def developer_key(self, key):
        if key is not None:
            return self.set_developer_key(key)
        else:
            return self.get_developer_key()

    # Zigbee commands
    @command()
    def zigbee(self):
        click.echo("Zigbee channel: %s" % self.get_zigbee_channel())

    @command()
    def get_zigbee_version(self):
        """timeouts on device"""
        return self.send("get_zigbee_device_version")

    @command(click.argument("channel"))
    def set_zigbee_channel(self, channel):
        """Set zigbee channel."""
        return self.send("set_zigbee_channel", [channel])

    def get_zigbee_channel(self):
        """Return currently used zigbee channel."""
        return self.send("get_zigbee_channel")[0]

    @command(click.argument("timeout", type=int))
    def zigbee_pair(self, timeout):
        """Start pairing, use 0 to disable"""
        return self.send("start_zigbee_join", [timeout])

    @command()
    def send_to_zigbee(self):
        """differs from write attribute? params?"""
        return self.send("send_to_zigbee")

    @command()
    def read_zigbee_eep(self):
        """read eeprom?"""
        return self.send("read_zig_eep", [0])  # 'ok'

    @command()
    def read_zigbee_attribute(self):
        """read zg"""
        return self.send("read_zigbee_attribute", [0x0000, 0x0080])

    @command()
    def write_zigbee_attribute(self):
        """unknown params"""
        return self.send("write_zigbee_attribute")

    @command()
    def zigbee_unpair_all(self):
        """Unpair all devices."""
        return self.send("remove_all_device")

    @command(click.argument("sid"))
    def zigbee_unpair(self, sid):
        """Unpair a device."""
        # get a device obj an call dev.unpair()
        raise NotImplementedError()

    @command()
    def welcome(self):
        """unknown"""
        return self.send("welcome")

    @command()
    def get_scenes(self):
        """Returns a list of rooms/Ids associated devices?"""
        # {'cur_page': 0,
        #  'fac_scene_enable': 0,
        #  'bind_num': 4,
        #  'page': [{'id': 461316256}, {'id': 461316667}, {'id': 462261531}, {'id': 462541389}],
        #  'total_page': 1}
        page = 0  # iterate over all pages
        return self.send("get_lumi_bind", ["scene", page])

    @command()
    def list_bind(self):
        """params error w/o params, unknown"""
        return self.send("list_bind", [0])

    @command()
    def remove_all_bind(self):
        """removes connected devices? or network?"""
        raise NotImplementedError()
        return self.send("remove_all_bind")

    @command()
    def occupy_sensor_cfg_get(self):
        """method not found"""
        return self.send("occupy_sensor_cfg_get")

    @command()
    def get_system_data(self):
        """doesn't seem to work w/o internet"""
        return self.send("get_sys_data")

    @command()
    def toggle_plug(self):
        """no clue"""
        return self.send("toggle_plug")

    @command()
    def toggle_device(self):
        """no clue"""
        return self.send("toggle_device")

    @command()
    def get_illumination(self):
        """lux?"""
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
