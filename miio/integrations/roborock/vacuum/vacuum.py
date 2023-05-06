import contextlib
import datetime
import enum
import json
import logging
import math
import os
import pathlib
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Type

import click
import pytz
from appdirs import user_cache_dir

from miio.click_common import (
    DeviceGroup,
    EnumType,
    GlobalContextObject,
    LiteralParamType,
    command,
)
from miio.device import Device, DeviceInfo
from miio.devicestatus import DeviceStatus, action
from miio.exceptions import DeviceInfoUnavailableException, UnsupportedFeatureException
from miio.identifiers import VacuumId

from .updatehelper import UpdateHelper
from .vacuum_enums import (
    CarpetCleaningMode,
    Consumable,
    DustCollectionMode,
    FanspeedE2,
    FanspeedEnum,
    FanspeedS7,
    FanspeedS7_Maxv,
    FanspeedV1,
    FanspeedV2,
    FanspeedV3,
    MopIntensity,
    MopMode,
    TimerState,
    WaterFlow,
)
from .vacuumcontainers import (
    CarpetModeStatus,
    CleaningDetails,
    CleaningSummary,
    ConsumableStatus,
    DNDStatus,
    MapList,
    MopDryerSettings,
    SoundInstallStatus,
    SoundStatus,
    Timer,
    VacuumStatus,
)

_LOGGER = logging.getLogger(__name__)


ROCKROBO_V1 = "rockrobo.vacuum.v1"
ROCKROBO_S4 = "roborock.vacuum.s4"
ROCKROBO_S4_MAX = "roborock.vacuum.a19"
ROCKROBO_S5 = "roborock.vacuum.s5"
ROCKROBO_S5_MAX = "roborock.vacuum.s5e"
ROCKROBO_S6 = "roborock.vacuum.s6"
ROCKROBO_T6 = "roborock.vacuum.t6"  # cn s6
ROCKROBO_E4 = "roborock.vacuum.a01"
ROCKROBO_S6_PURE = "roborock.vacuum.a08"
ROCKROBO_T7 = "roborock.vacuum.a11"  # cn s7
ROCKROBO_T7S = "roborock.vacuum.a14"
ROCKROBO_T7SPLUS = "roborock.vacuum.a23"
ROCKROBO_S7_MAXV = "roborock.vacuum.a27"
ROCKROBO_S7_PRO_ULTRA = "roborock.vacuum.a62"
ROCKROBO_Q5 = "roborock.vacuum.a34"
ROCKROBO_Q7_MAX = "roborock.vacuum.a38"
ROCKROBO_Q7PLUS = "roborock.vacuum.a40"
ROCKROBO_G10S = "roborock.vacuum.a46"
ROCKROBO_G10 = "roborock.vacuum.a29"

ROCKROBO_S7 = "roborock.vacuum.a15"
ROCKROBO_S6_MAXV = "roborock.vacuum.a10"
ROCKROBO_E2 = "roborock.vacuum.e2"
ROCKROBO_1S = "roborock.vacuum.m1s"
ROCKROBO_C1 = "roborock.vacuum.c1"
ROCKROBO_WILD = "roborock.vacuum.*"  # wildcard

SUPPORTED_MODELS = [
    ROCKROBO_V1,
    ROCKROBO_S4,
    ROCKROBO_S4_MAX,
    ROCKROBO_E4,
    ROCKROBO_S5,
    ROCKROBO_S5_MAX,
    ROCKROBO_S6,
    ROCKROBO_T6,
    ROCKROBO_S6_PURE,
    ROCKROBO_T7,
    ROCKROBO_T7S,
    ROCKROBO_T7SPLUS,
    ROCKROBO_S7,
    ROCKROBO_S7_MAXV,
    ROCKROBO_S7_PRO_ULTRA,
    ROCKROBO_Q5,
    ROCKROBO_Q7_MAX,
    ROCKROBO_Q7PLUS,
    ROCKROBO_G10,
    ROCKROBO_G10S,
    ROCKROBO_S6_MAXV,
    ROCKROBO_E2,
    ROCKROBO_1S,
    ROCKROBO_C1,
    ROCKROBO_WILD,
]

AUTO_EMPTY_MODELS = [
    ROCKROBO_S7,
    ROCKROBO_S7_MAXV,
    ROCKROBO_Q7_MAX,
]


class RoborockVacuum(Device):
    """Main class for roborock vacuums (roborock.vacuum.*)."""

    _supported_models = SUPPORTED_MODELS
    _auto_empty_models = AUTO_EMPTY_MODELS

    def __init__(
        self,
        ip: str,
        token: Optional[str] = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: Optional[int] = None,
        *,
        model=None,
    ):
        super().__init__(
            ip, token, start_id, debug, lazy_discover, timeout, model=model
        )
        self.manual_seqnum = -1
        self._maps: Optional[MapList] = None
        self._map_enum_cache = None
        self._status_helper = UpdateHelper(self.vacuum_status)
        self._status_helper.add_update_method("consumables", self.consumable_status)
        self._status_helper.add_update_method("dnd_status", self.dnd_status)
        self._status_helper.add_update_method("clean_history", self.clean_history)
        self._status_helper.add_update_method("last_clean", self.last_clean_details)
        self._status_helper.add_update_method("mop_dryer", self.mop_dryer_settings)

    def send(
        self,
        command: str,
        parameters: Optional[Any] = None,
        retry_count: Optional[int] = None,
        *,
        extra_parameters=None,
    ) -> Any:
        """Send command to the device.

        This is overridden to raise an exception on unknown methods.
        """
        res = super().send(
            command, parameters, retry_count, extra_parameters=extra_parameters
        )
        if res == "unknown_method":
            raise UnsupportedFeatureException(
                f"Command {command} is not supported by the device"
            )
        return res

    @command()
    def start(self):
        """Start cleaning."""
        return self.send("app_start")

    @command()
    @action(name="Stop cleaning", id=VacuumId.Stop)
    def stop(self):
        """Stop cleaning.

        Note, prefer 'pause' instead of this for wider support. Some newer vacuum models
        do not support this command.
        """
        return self.send("app_stop")

    @command()
    @action(name="Spot cleaning", id=VacuumId.Spot)
    def spot(self):
        """Start spot cleaning."""
        return self.send("app_spot")

    @command()
    @action(name="Pause cleaning", id=VacuumId.Pause)
    def pause(self):
        """Pause cleaning."""
        return self.send("app_pause")

    @command()
    @action(name="Start cleaning", id=VacuumId.Start)
    def resume_or_start(self):
        """A shortcut for resuming or starting cleaning."""
        status = self.status()
        if status.in_zone_cleaning and (status.is_paused or status.got_error):
            return self.resume_zoned_clean()
        if status.in_segment_cleaning and (status.is_paused or status.got_error):
            return self.resume_segment_clean()

        return self.start()

    def _fetch_info(self) -> DeviceInfo:
        """Return info about the device.

        This is overrides the base class info to account for gen1 devices that do not
        respond to info query properly when not connected to the cloud.
        """
        try:
            info = super()._fetch_info()
            return info
        except (TypeError, DeviceInfoUnavailableException):
            # cloud-blocked gen1 vacuums will not return proper payloads
            def create_dummy_mac(addr):
                """Returns a dummy mac for a given IP address.

                This squats the FF:FF:<first octet> OUI for a dummy mac presentation to
                allow presenting a unique identifier for homeassistant.
                """
                from ipaddress import ip_address

                ip_to_mac = ":".join(
                    [f"{hex(x).replace('0x', ''):0>2}" for x in ip_address(addr).packed]
                )
                return f"FF:FF:{ip_to_mac}"

            dummy_v1 = DeviceInfo(
                {
                    "model": ROCKROBO_V1,
                    "token": self.token,
                    "netif": {"localIp": self.ip},
                    "mac": create_dummy_mac(self.ip),
                    "fw_ver": "1.0_nocloud",
                    "hw_ver": "1st gen non-cloud hw",
                }
            )

            self._info = dummy_v1
            _LOGGER.debug(
                "Unable to query info, falling back to dummy %s", dummy_v1.model
            )
            return self._info

    @command()
    @action(name="Home", id=VacuumId.ReturnHome)
    def home(self):
        """Stop cleaning and return home."""

        PAUSE_BEFORE_HOME = [
            ROCKROBO_V1,
        ]

        if self.model in PAUSE_BEFORE_HOME:
            self.send("app_pause")

        return self.send("app_charge")

    @command(click.argument("x_coord", type=int), click.argument("y_coord", type=int))
    def goto(self, x_coord: int, y_coord: int):
        """Go to specific target.

        :param int x_coord: x coordinate
        :param int y_coord: y coordinate
        """
        return self.send("app_goto_target", [x_coord, y_coord])

    @command(click.argument("zones", type=LiteralParamType(), required=True))
    def zoned_clean(self, zones: List):
        """Clean zones.

        :param List zones: List of zones to clean: [[x1,y1,x2,y2, iterations],[x1,y1,x2,y2, iterations]]
        """
        return self.send("app_zoned_clean", zones)

    @command()
    def resume_zoned_clean(self):
        """Resume zone cleaning after being paused."""
        return self.send("resume_zoned_clean")

    @command()
    def manual_start(self):
        """Start manual control mode."""
        self.manual_seqnum = 0
        return self.send("app_rc_start")

    @command()
    def manual_stop(self):
        """Stop manual control mode."""
        self.manual_seqnum = 0
        return self.send("app_rc_end")

    MANUAL_ROTATION_MAX = 180
    MANUAL_ROTATION_MIN = -MANUAL_ROTATION_MAX
    MANUAL_VELOCITY_MAX = 0.3
    MANUAL_VELOCITY_MIN = -MANUAL_VELOCITY_MAX
    MANUAL_DURATION_DEFAULT = 1500

    @command(
        click.argument("rotation", type=int),
        click.argument("velocity", type=float),
        click.argument(
            "duration", type=int, required=False, default=MANUAL_DURATION_DEFAULT
        ),
    )
    def manual_control_once(
        self, rotation: int, velocity: float, duration: int = MANUAL_DURATION_DEFAULT
    ):
        """Starts the remote control mode and executes the action once before
        deactivating the mode."""
        number_of_tries = 3
        self.manual_start()
        while number_of_tries > 0:
            if self.status().state_code == 7:
                time.sleep(5)
                self.manual_control(rotation, velocity, duration)
                time.sleep(5)
                return self.manual_stop()

            time.sleep(2)
            number_of_tries -= 1

    @command(
        click.argument("rotation", type=int),
        click.argument("velocity", type=float),
        click.argument(
            "duration", type=int, required=False, default=MANUAL_DURATION_DEFAULT
        ),
    )
    def manual_control(
        self, rotation: int, velocity: float, duration: int = MANUAL_DURATION_DEFAULT
    ):
        """Give a command over manual control interface."""
        if rotation < self.MANUAL_ROTATION_MIN or rotation > self.MANUAL_ROTATION_MAX:
            raise ValueError(
                "Given rotation is invalid, should be ]%s, %s[, was %s"
                % (self.MANUAL_ROTATION_MIN, self.MANUAL_ROTATION_MAX, rotation)
            )
        if velocity < self.MANUAL_VELOCITY_MIN or velocity > self.MANUAL_VELOCITY_MAX:
            raise ValueError(
                "Given velocity is invalid, should be ]%s, %s[, was: %s"
                % (self.MANUAL_VELOCITY_MIN, self.MANUAL_VELOCITY_MAX, velocity)
            )

        self.manual_seqnum += 1
        params = {
            "omega": round(math.radians(rotation), 1),
            "velocity": velocity,
            "duration": duration,
            "seqnum": self.manual_seqnum,
        }

        self.send("app_rc_move", [params])

    @command()
    def status(self) -> DeviceStatus:
        """Return status of the vacuum."""
        return self._status_helper.status()

    @command()
    def vacuum_status(self) -> VacuumStatus:
        """Return only status of the vacuum."""
        return VacuumStatus(self.send("get_status")[0])

    def enable_log_upload(self):
        raise NotImplementedError("unknown parameters")
        # return self.send("enable_log_upload")

    @command()
    def log_upload_status(self):
        # {"result": [{"log_upload_status": 7}], "id": 1}
        return self.send("get_log_upload_status")

    @command()
    def consumable_status(self) -> ConsumableStatus:
        """Return information about consumables."""
        return ConsumableStatus(self.send("get_consumable")[0])

    @command(click.argument("consumable", type=Consumable))
    def consumable_reset(self, consumable: Consumable):
        """Reset consumable information."""
        return self.send("reset_consumable", [consumable.value])

    @command()
    def map(self):
        """Return map token."""
        # returns ['retry'] without internet
        return self.send("get_map_v1")

    @command()
    def get_maps(self) -> MapList:
        """Return list of maps."""
        if self._maps is not None:
            return self._maps

        self._maps = MapList(self.send("get_multi_maps_list")[0])
        return self._maps

    def _map_enum(self) -> Optional[Type[Enum]]:
        """Enum of the available map names."""
        if self._map_enum_cache is not None:
            return self._map_enum_cache

        maps = self.get_maps()

        self._map_enum_cache = enum.Enum("map_enum", maps.map_name_dict)
        return self._map_enum_cache

    @command(click.argument("map_id", type=int))
    def load_map(
        self,
        map_enum: Optional[enum.Enum] = None,
        map_id: Optional[int] = None,
    ):
        """Change the current map used."""
        if map_enum is None and map_id is None:
            raise ValueError("Either map_enum or map_id is required.")

        if map_enum is not None:
            map_id = map_enum.value

        return self.send("load_multi_map", [map_id])[0] == "ok"

    @command(click.argument("start", type=bool))
    def edit_map(self, start):
        """Start map editing?"""
        if start:
            return self.send("start_edit_map")[0] == "ok"
        else:
            return self.send("end_edit_map")[0] == "ok"

    @command(click.option("--version", default=1))
    def fresh_map(self, version):
        """Return fresh map?"""
        if version not in [1, 2]:
            raise ValueError("Unknown map version: %s" % version)

        if version == 1:
            return self.send("get_fresh_map")
        elif version == 2:
            return self.send("get_fresh_map_v2")

    @command(click.option("--version", default=1))
    def persist_map(self, version):
        """Return fresh map?"""
        if version not in [1, 2]:
            raise ValueError("Unknown map version: %s" % version)

        if version == 1:
            return self.send("get_persist_map")
        elif version == 2:
            return self.send("get_persist_map_v2")

    @command(
        click.argument("x1", type=int),
        click.argument("y1", type=int),
        click.argument("x2", type=int),
        click.argument("y2", type=int),
    )
    def create_software_barrier(self, x1, y1, x2, y2):
        """Create software barrier (gen2 only?).

        NOTE: Multiple nogo zones and barriers could be added by passing
        a list of them to save_map.

        Requires new fw version.
        3.3.9_001633+?
        """
        # First parameter indicates the type, 1 = barrier
        payload = [1, x1, y1, x2, y2]
        return self.send("save_map", payload)[0] == "ok"

    @command(
        click.argument("x1", type=int),
        click.argument("y1", type=int),
        click.argument("x2", type=int),
        click.argument("y2", type=int),
        click.argument("x3", type=int),
        click.argument("y3", type=int),
        click.argument("x4", type=int),
        click.argument("y4", type=int),
    )
    def create_nogo_zone(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Create a rectangular no-go zone (gen2 only?).

        NOTE: Multiple nogo zones and barriers could be added by passing
        a list of them to save_map.

        Requires new fw version.
        3.3.9_001633+?
        """
        # First parameter indicates the type, 0 = zone
        payload = [0, x1, y1, x2, y2, x3, y3, x4, y4]
        return self.send("save_map", payload)[0] == "ok"

    @command(click.argument("enable", type=bool))
    def enable_lab_mode(self, enable):
        """Enable persistent maps and software barriers.

        This is required to use create_nogo_zone and create_software_barrier commands.
        """
        return self.send("set_lab_status", int(enable))["ok"]

    @command()
    def clean_history(self) -> CleaningSummary:
        """Return generic cleaning history."""
        return CleaningSummary(self.send("get_clean_summary"))

    @command()
    def last_clean_details(self) -> Optional[CleaningDetails]:
        """Return details from the last cleaning.

        Returns None if there has been no cleanups.
        """
        history = self.clean_history()
        if not history.ids:
            return None

        last_clean_id = history.ids.pop(0)
        return self.clean_details(last_clean_id)

    @command(
        click.argument("id_", type=int, metavar="ID"),
    )
    def clean_details(self, id_: int) -> Optional[CleaningDetails]:
        """Return details about specific cleaning."""
        details = self.send("get_clean_record", [id_])

        if not details:
            _LOGGER.warning("No cleaning record found for id %s", id_)
            return None

        res = CleaningDetails(details.pop())
        return res

    @command()
    @action(name="Find robot", id=VacuumId.Locate)
    def find(self):
        """Find the robot."""
        return self.send("find_me", [""])

    @command()
    def timer(self) -> List[Timer]:
        """Return a list of timers."""
        timers: List[Timer] = list()
        res = self.send("get_timer", [""])
        if not res:
            return timers

        timezone = pytz.timezone(self.timezone())
        for rec in res:
            try:
                timers.append(Timer(rec, timezone=timezone))
            except Exception as ex:
                _LOGGER.warning("Unable to add timer for %s: %s", rec, ex)

        return timers

    @command(
        click.argument("cron"),
        click.argument("command", required=False, default=""),
        click.argument("parameters", required=False, default=""),
        click.argument("timer_id", required=False, default=None),
    )
    def add_timer(self, cron: str, command: str, parameters: str, timer_id: str):
        """Add a timer.

        :param cron: schedule in cron format
        :param command: ignored by the vacuum.
        :param parameters: ignored by the vacuum.
        """
        if not timer_id:
            timer_id = str(int(round(time.time() * 1000)))
        return self.send("set_timer", [[timer_id, [cron, [command, parameters]]]])

    @command(click.argument("timer_id", type=str))
    def delete_timer(self, timer_id: str):
        """Delete a timer with given ID.

        :param str timer_id: Timer ID
        """
        return self.send("del_timer", [timer_id])

    @command(
        click.argument("timer_id", type=str), click.argument("mode", type=TimerState)
    )
    def update_timer(self, timer_id: str, mode: TimerState):
        """Update a timer with given ID.

        :param str timer_id: Timer ID
        :param TimerState mode: either On or Off
        """
        if mode != TimerState.On and mode != TimerState.Off:
            raise ValueError("Only 'On' or 'Off' are  allowed")
        return self.send("upd_timer", [timer_id, mode.value])

    @command()
    def dnd_status(self) -> DNDStatus:
        """Returns do-not-disturb status."""
        # {'result': [{'enabled': 1, 'start_minute': 0, 'end_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}], 'id': 1}
        return DNDStatus(self.send("get_dnd_timer")[0])

    @command(
        click.argument("start_hr", type=int),
        click.argument("start_min", type=int),
        click.argument("end_hr", type=int),
        click.argument("end_min", type=int),
    )
    def set_dnd(self, start_hr: int, start_min: int, end_hr: int, end_min: int):
        """Set do-not-disturb.

        :param int start_hr: Start hour
        :param int start_min: Start minute
        :param int end_hr: End hour
        :param int end_min: End minute
        """
        return self.send("set_dnd_timer", [start_hr, start_min, end_hr, end_min])

    @command()
    def disable_dnd(self):
        """Disable do-not-disturb."""
        return self.send("close_dnd_timer", [""])

    @command(click.argument("speed", type=int))
    def set_fan_speed(self, speed: int):
        """Set fan speed.

        :param int speed: Fan speed to set
        """
        # speed = [38, 60 or 77]
        return self.send("set_custom_mode", [speed])

    @command()
    def fan_speed(self):
        """Return fan speed."""
        return self.send("get_custom_mode")[0]

    @command()
    def fan_speed_presets(self) -> Dict[str, int]:
        """Return available fan speed presets."""

        def _enum_as_dict(cls):
            return {x.name: x.value for x in list(cls)}

        if self.model is None:
            return _enum_as_dict(FanspeedV1)

        fanspeeds: Type[FanspeedEnum] = FanspeedV1

        if self.model == ROCKROBO_V1:
            _LOGGER.debug("Got robov1, checking for firmware version")
            fw_version = self.info().firmware_version
            version, build = fw_version.split("_")
            version = tuple(map(int, version.split(".")))
            if version >= (3, 5, 8):
                fanspeeds = FanspeedV3
            elif version == (3, 5, 7):
                fanspeeds = FanspeedV2
            else:
                fanspeeds = FanspeedV1
        elif self.model == ROCKROBO_E2:
            fanspeeds = FanspeedE2
        elif self.model == ROCKROBO_S7:
            fanspeeds = FanspeedS7
        elif self.model == ROCKROBO_S7_MAXV:
            fanspeeds = FanspeedS7_Maxv
        else:
            fanspeeds = FanspeedV2

        _LOGGER.debug("Using fanspeeds %s for %s", fanspeeds, self.model)

        return _enum_as_dict(fanspeeds)

    @command(click.argument("speed", type=int))
    def set_fan_speed_preset(self, speed_preset: int) -> None:
        """Set fan speed preset speed."""
        if speed_preset not in self.fan_speed_presets().values():
            raise ValueError(
                f"Invalid preset speed {speed_preset}, not in: {self.fan_speed_presets().values()}"
            )
        return self.send("set_custom_mode", [speed_preset])

    @command()
    def sound_info(self):
        """Get voice settings."""
        return SoundStatus(self.send("get_current_sound")[0])

    @command(
        click.argument("url"),
        click.argument("md5sum"),
        click.argument("sound_id", type=int),
    )
    def install_sound(self, url: str, md5sum: str, sound_id: int):
        """Install sound from the given url."""
        payload = {"url": url, "md5": md5sum, "sid": int(sound_id)}
        return SoundInstallStatus(self.send("dnld_install_sound", payload)[0])

    @command()
    def sound_install_progress(self):
        """Get sound installation progress."""
        return SoundInstallStatus(self.send("get_sound_progress")[0])

    @command()
    def sound_volume(self) -> int:
        """Get sound volume."""
        return self.send("get_sound_volume")[0]

    @command(click.argument("vol", type=int))
    def set_sound_volume(self, vol: int):
        """Set sound volume [0-100]."""
        return self.send("change_sound_volume", [vol])

    @command()
    @action(name="Test sound volume")
    def test_sound_volume(self):
        """Test current sound volume."""
        return self.send("test_sound_volume")

    @command()
    def serial_number(self):
        """Get serial number."""
        serial = self.send("get_serial_number")
        if isinstance(serial, list):
            return serial[0]["serial_number"]
        return serial

    @command()
    def locale(self):
        """Return locale information."""
        return self.send("app_get_locale")

    @command()
    def timezone(self):
        """Get the timezone."""
        res = self.send("get_timezone")

        def _fallback_timezone(data):
            fallback = "UTC"
            _LOGGER.error(
                "Unsupported timezone format (%s), falling back to %s", data, fallback
            )
            return fallback

        if isinstance(res, int):
            return _fallback_timezone(res)

        res = res[0]
        if isinstance(res, dict):
            # Xiaowa E25 example
            # {'olson': 'Europe/Berlin', 'posix': 'CET-1CEST,M3.5.0,M10.5.0/3'}
            if "olson" not in res:
                return _fallback_timezone(res)

            return res["olson"]

        return res

    def set_timezone(self, new_zone):
        """Set the timezone."""
        return self.send("set_timezone", [new_zone])[0] == "ok"

    def configure_wifi(self, ssid, password, uid=0, timezone=None):
        """Configure the wifi settings."""
        extra_params = {}
        if timezone is not None:
            now = datetime.datetime.now(pytz.timezone(timezone))
            offset_as_float = now.utcoffset().total_seconds() / 60 / 60
            extra_params["tz"] = timezone
            extra_params["gmt_offset"] = offset_as_float

        return super().configure_wifi(ssid, password, uid, extra_params)

    @command()
    def carpet_mode(self) -> CarpetModeStatus:
        """Get carpet mode settings."""
        return CarpetModeStatus(self.send("get_carpet_mode")[0])

    @command(
        click.argument("enabled", required=True, type=bool),
        click.argument("stall_time", required=False, default=10, type=int),
        click.argument("low", required=False, default=400, type=int),
        click.argument("high", required=False, default=500, type=int),
        click.argument("integral", required=False, default=450, type=int),
    )
    def set_carpet_mode(
        self,
        enabled: bool,
        stall_time: int = 10,
        low: int = 400,
        high: int = 500,
        integral: int = 450,
    ):
        """Set the carpet mode."""
        click.echo("Setting carpet mode: %s" % enabled)
        data = {
            "enable": int(enabled),
            "stall_time": stall_time,
            "current_low": low,
            "current_high": high,
            "current_integral": integral,
        }
        return self.send("set_carpet_mode", [data])[0] == "ok"

    @command()
    def carpet_cleaning_mode(self) -> Optional[CarpetCleaningMode]:
        """Get carpet cleaning mode/avoidance setting."""
        try:
            return CarpetCleaningMode(
                self.send("get_carpet_clean_mode")[0]["carpet_clean_mode"]
            )
        except Exception as err:
            _LOGGER.warning("Error while requesting carpet clean mode: %s", err)
            return None

    @command(click.argument("mode", type=EnumType(CarpetCleaningMode)))
    def set_carpet_cleaning_mode(self, mode: CarpetCleaningMode):
        """Set carpet cleaning mode/avoidance setting."""
        return (
            self.send("set_carpet_clean_mode", {"carpet_clean_mode": mode.value})[0]
            == "ok"
        )

    @command()
    def dust_collection_mode(self) -> Optional[DustCollectionMode]:
        """Get the dust collection mode setting."""
        self._verify_auto_empty_support()
        try:
            return DustCollectionMode(self.send("get_dust_collection_mode")["mode"])
        except Exception as err:
            _LOGGER.warning("Error while requesting dust collection mode: %s", err)
            return None

    @command(click.argument("enabled", required=True, type=bool))
    def set_dust_collection(self, enabled: bool) -> bool:
        """Turn automatic dust collection on or off."""
        self._verify_auto_empty_support()
        return (
            self.send("set_dust_collection_switch_status", {"status": int(enabled)})[0]
            == "ok"
        )

    @command(click.argument("mode", required=True, type=EnumType(DustCollectionMode)))
    def set_dust_collection_mode(self, mode: DustCollectionMode) -> bool:
        """Set dust collection mode setting."""
        self._verify_auto_empty_support()
        return self.send("set_dust_collection_mode", {"mode": mode.value})[0] == "ok"

    @command()
    @action(name="Start dust collection", icon="mdi:turbine")
    def start_dust_collection(self):
        """Activate automatic dust collection."""
        self._verify_auto_empty_support()
        return self.send("app_start_collect_dust")

    @command()
    @action(name="Stop dust collection", icon="mdi:turbine")
    def stop_dust_collection(self):
        """Abort in progress dust collection."""
        self._verify_auto_empty_support()
        return self.send("app_stop_collect_dust")

    def _verify_auto_empty_support(self) -> None:
        if self.model not in self._auto_empty_models:
            raise UnsupportedFeatureException("Device does not support auto emptying")

    @command()
    def stop_zoned_clean(self):
        """Stop cleaning a zone."""
        return self.send("stop_zoned_clean")

    @command()
    def stop_segment_clean(self):
        """Stop cleaning a segment."""
        return self.send("stop_segment_clean")

    @command()
    def resume_segment_clean(self):
        """Resuming cleaning a segment."""
        return self.send("resume_segment_clean")

    @command(click.argument("segments", type=LiteralParamType(), required=True))
    @command(click.argument("repeat", type=int, required=False, default=1))
    def segment_clean(self, segments: List, repeat: int = 1):
        """Clean segments.

        :param List segments: List of segments to clean: [16,17,18]
        :param int repeat: Count of iterations
        """
        return self.send(
            "app_segment_clean", [{"segments": segments, "repeat": repeat}]
        )

    @command()
    def get_room_mapping(self):
        """Retrieves a list of segments."""
        return self.send("get_room_mapping")

    @command()
    def get_backup_maps(self):
        """Get backup maps."""
        return self.send("get_recover_maps")

    @command(click.argument("id", type=int))
    def use_backup_map(self, id: int):
        """Set backup map."""
        click.echo("Setting the map %s as active" % id)
        return self.send("recover_map", [id])

    @command()
    def get_segment_status(self):
        """Get the status of a segment."""
        return self.send("get_segment_status")

    def name_segment(self):
        raise NotImplementedError("unknown parameters")
        # return self.send("name_segment")

    def merge_segment(self):
        raise NotImplementedError("unknown parameters")
        # return self.send("merge_segment")

    def split_segment(self):
        raise NotImplementedError("unknown parameters")
        # return self.send("split_segment")

    @command()
    def waterflow(self) -> WaterFlow:
        """Get water flow setting."""
        flow_raw = self.send("get_water_box_custom_mode")
        if self.model == ROCKROBO_Q7_MAX:
            flow_value = flow_raw["water_box_mode"]
            # There is additional "distance_off" key which
            # specifies custom level with water_box_mode=207.
            # App has 30 levels (1-30), distance_off = 210 - 5 * level
        else:
            flow_value = flow_raw[0]
        return WaterFlow(flow_value)

    @command(click.argument("waterflow", type=EnumType(WaterFlow)))
    def set_waterflow(self, waterflow: WaterFlow):
        """Set water flow setting."""
        if self.model == ROCKROBO_Q7_MAX:
            return self.send(
                "set_water_box_custom_mode",
                {"water_box_mode": waterflow.value, "distance_off": 205},
            )
        return self.send("set_water_box_custom_mode", [waterflow.value])

    @command()
    def mop_mode(self) -> Optional[MopMode]:
        """Get mop mode setting."""
        try:
            return MopMode(self.send("get_mop_mode")[0])
        except ValueError as err:
            _LOGGER.warning("Device returned unknown MopMode: %s", err)
            return None

    @command(click.argument("mop_mode", type=EnumType(MopMode)))
    def set_mop_mode(self, mop_mode: MopMode):
        """Set mop mode setting."""
        return self.send("set_mop_mode", [mop_mode.value])[0] == "ok"

    @command()
    def mop_intensity(self) -> MopIntensity:
        """Get mop scrub intensity setting."""
        if self.model not in [ROCKROBO_S7, ROCKROBO_S7_MAXV]:
            raise UnsupportedFeatureException(
                "Mop scrub intensity not supported by %s", self.model
            )

        return MopIntensity(self.send("get_water_box_custom_mode")[0])

    @command(click.argument("mop_intensity", type=EnumType(MopIntensity)))
    def set_mop_intensity(self, mop_intensity: MopIntensity):
        """Set mop scrub intensity setting."""
        if self.model not in [ROCKROBO_S7, ROCKROBO_S7_MAXV]:
            raise UnsupportedFeatureException(
                "Mop scrub intensity not supported by %s", self.model
            )

        return self.send("set_water_box_custom_mode", [mop_intensity.value])

    @command()
    def child_lock(self) -> bool:
        """Get child lock setting."""
        return self.send("get_child_lock_status")["lock_status"] == 1

    @command(click.argument("lock", type=bool))
    def set_child_lock(self, lock: bool) -> bool:
        """Set child lock setting."""
        return self.send("set_child_lock_status", {"lock_status": int(lock)})[0] == "ok"

    @command()
    def mop_dryer_settings(self) -> MopDryerSettings:
        """Get mop dryer settings."""
        return MopDryerSettings(self.send("app_get_dryer_setting"))

    @command(click.argument("enabled", type=bool))
    def set_mop_dryer_enabled(self, enabled: bool) -> bool:
        """Set mop dryer add-on enabled."""
        return self.send("app_set_dryer_setting", {"status": int(enabled)})[0] == "ok"

    @command(click.argument("dry_time", type=int))
    def set_mop_dryer_dry_time(self, dry_time_seconds: int) -> bool:
        """Set mop dryer add-on dry time."""
        return (
            self.send("app_set_dryer_setting", {"on": {"dry_time": dry_time_seconds}})[
                0
            ]
            == "ok"
        )

    @command()
    @action(name="Start mop washing", icon="mdi:wiper-wash")
    def start_mop_washing(self) -> bool:
        """Start mop washing."""
        return self.send("app_start_wash")[0] == "ok"

    @command()
    @action(name="Stop mop washing", icon="mdi:wiper-wash")
    def stop_mop_washing(self) -> bool:
        """Start mop washing."""
        return self.send("app_stop_wash")[0] == "ok"

    @command()
    @action(name="Start mop drying", icon="mdi:tumble-dryer")
    def start_mop_drying(self) -> bool:
        """Start mop drying."""
        return self.send("app_set_dryer_status", {"status": 1})[0] == "ok"

    @command()
    @action(name="Stop mop drying", icon="mdi:tumble-dryer")
    def stop_mop_drying(self) -> bool:
        """Stop mop drying."""
        return self.send("app_set_dryer_status", {"status": 0})[0] == "ok"

    @command()
    def firmware_features(self) -> List[int]:
        """Return a list of available firmware features.

        Information: https://github.com/marcelrv/XiaomiRobotVacuumProtocol/blob/master/fw_features.md
        Feel free to contribute information from your vacuum if it is not yet listed.
        """
        return self.send("get_fw_features")

    @classmethod
    def get_device_group(cls):
        @click.pass_context
        def callback(ctx, *args, id_file, **kwargs):
            gco = ctx.find_object(GlobalContextObject)
            if gco:
                kwargs["debug"] = gco.debug

            start_id = manual_seq = 0
            with contextlib.suppress(FileNotFoundError, TypeError, ValueError), open(
                id_file
            ) as f:
                x = json.load(f)
                start_id = x.get("seq", 0)
                manual_seq = x.get("manual_seq", 0)
                _LOGGER.debug("Read stored sequence ids: %s", x)

            ctx.obj = cls(*args, start_id=start_id, **kwargs)
            ctx.obj.manual_seqnum = manual_seq

        dg = DeviceGroup(
            cls,
            params=DeviceGroup.DEFAULT_PARAMS
            + [
                click.Option(
                    ["--id-file"],
                    type=click.Path(dir_okay=False, writable=True),
                    default=os.path.join(
                        user_cache_dir("python-miio"), "python-mirobo.seq"
                    ),
                )
            ],
            callback=callback,
        )

        @dg.result_callback()
        @dg.device_pass
        def cleanup(vac: RoborockVacuum, *args, **kwargs):
            if vac.ip is None:  # dummy Device for discovery, skip teardown
                return
            id_file = kwargs["id_file"]
            seqs = {"seq": vac._protocol.raw_id, "manual_seq": vac.manual_seqnum}
            _LOGGER.debug("Writing %s to %s", seqs, id_file)
            path_obj = pathlib.Path(id_file)
            cache_dir = path_obj.parents[0]
            cache_dir.mkdir(parents=True, exist_ok=True)
            with open(id_file, "w") as f:
                json.dump(seqs, f)

        return dg
