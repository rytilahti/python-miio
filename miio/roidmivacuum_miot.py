"""Vacuum Eve Plus (roidmi.vacuum.v60)"""


import json
import logging
import math
from datetime import timedelta
from enum import Enum

import click

from .click_common import EnumType, command
from .miot_device import DeviceStatus, MiotDevice, MiotMapping
from .vacuumcontainers import DNDStatus

_LOGGER = logging.getLogger(__name__)

_MAPPING: MiotMapping = {
    "battery_level": {"siid": 3, "piid": 1},
    "charging_state": {"siid": 3, "piid": 2},
    "error_code": {"siid": 2, "piid": 2},
    "state": {"siid": 2, "piid": 1},
    "filter_life_level": {"siid": 10, "piid": 1},
    "filter_left_minutes": {"siid": 10, "piid": 2},
    "main_brush_left_minutes": {"siid": 11, "piid": 1},
    "main_brush_life_level": {"siid": 11, "piid": 2},
    "side_brushes_left_minutes": {"siid": 12, "piid": 1},
    "side_brushes_life_level": {"siid": 12, "piid": 2},
    "sensor_dirty_time_left_minutes": {
        "siid": 15,
        "piid": 1,
    },  # named brush_left_time in the spec
    "sensor_dirty_remaning_level": {"siid": 15, "piid": 2},
    "sweep_mode": {"siid": 14, "piid": 1},
    "fanspeed_mode": {"siid": 2, "piid": 4},
    "sweep_type": {"siid": 2, "piid": 8},
    "path_mode": {"siid": 13, "piid": 8},
    "mop_present": {"siid": 8, "piid": 1},
    "work_station_freq": {"siid": 8, "piid": 2},  # Range: [0, 3, 1]
    "timing": {"siid": 8, "piid": 6},
    "clean_area": {"siid": 8, "piid": 7},  # uint32
    # "uid": {"siid": 8, "piid": 8},  # str - This UID is unknown
    "auto_boost": {"siid": 8, "piid": 9},
    "forbid_mode": {"siid": 8, "piid": 10},  # str
    "water_level": {"siid": 8, "piid": 11},
    "total_clean_time_sec": {"siid": 8, "piid": 13},
    "total_clean_areas": {"siid": 8, "piid": 14},
    "clean_counts": {"siid": 8, "piid": 18},
    "clean_time_sec": {"siid": 8, "piid": 19},
    "double_clean": {"siid": 8, "piid": 20},
    # "edge_sweep": {"siid": 8, "piid": 21}, # 2021-07-11: Roidmi Eve is not changing behavior when this bool is changed
    "led_switch": {"siid": 8, "piid": 22},
    "lidar_collision": {"siid": 8, "piid": 23},
    "station_key": {"siid": 8, "piid": 24},
    "station_led": {"siid": 8, "piid": 25},
    "current_audio": {"siid": 8, "piid": 26},
    # "progress": {"siid": 8, "piid": 28}, # 2021-07-11: this is part of the spec, but not implemented in Roidme Eve
    "station_type": {"siid": 8, "piid": 29},  # uint32
    # "voice_conf": {"siid": 8, "piid": 30}, # Always return file not exist !!!
    # "switch_status": {"siid": 2, "piid": 10}, # Enum with only one value: Open
    "volume": {"siid": 9, "piid": 1},
    "mute": {"siid": 9, "piid": 2},
    "start": {"siid": 2, "aiid": 1},
    "stop": {"siid": 2, "aiid": 2},
    "start_room_sweep": {"siid": 2, "aiid": 3},
    "start_sweep": {"siid": 14, "aiid": 1},
    "home": {"siid": 3, "aiid": 1},
    "identify": {"siid": 8, "aiid": 1},
    "start_station_dust_collection": {"siid": 8, "aiid": 6},
    "set_voice": {"siid": 8, "aiid": 12},
    "reset_filter_life": {"siid": 10, "aiid": 1},
    "reset_main_brush_life": {"siid": 11, "aiid": 1},
    "reset_side_brushes_life": {"siid": 12, "aiid": 1},
    "reset_sensor_dirty_life": {"siid": 15, "aiid": 1},
}


class ChargingState(Enum):
    Unknown = -1
    Charging = 1
    Discharging = 2
    NotChargeable = 4


class FanSpeed(Enum):
    Unknown = -1
    Silent = 1
    Basic = 2
    Strong = 3
    FullSpeed = 4
    Sweep = 0


class SweepType(Enum):
    Unknown = -1
    Sweep = 0
    Mop = 1
    MopAndSweep = 2


class PathMode(Enum):
    Unknown = -1
    Normal = 0
    YMopping = 1
    RepeatMopping = 2


class WaterLevel(Enum):
    Unknown = -1
    First = 1
    Second = 2
    Three = 3
    Fourth = 4
    Mop = 0


class SweepMode(Enum):
    Unknown = -1
    Total = 1
    Area = 2
    Curpoint = 3
    Point = 4
    Smart = 7
    AmartArea = 8
    DepthTotal = 9
    AlongWall = 10
    Idle = 0


error_codes = {
    0: "NoFaults",
    1: "LowBatteryFindCharger",
    2: "LowBatteryAndPoweroff",
    3: "WheelRap",
    4: "CollisionError",
    5: "TileDoTask",
    6: "LidarPointError",
    7: "FrontWallError",
    8: "PsdDirty",
    9: "MiddleBrushFatal",
    10: "SideBrush",
    11: "FanSpeedError",
    12: "LidarCover",
    13: "GarbageBoxFull",
    14: "GarbageBoxOut",
    15: "GarbageBoxFullOut",
    16: "PhysicalTrapped",
    17: "PickUpDoTask",
    18: "NoWaterBoxDoTask",
    19: "WaterBoxEmpty",
    20: "CleanCannotArrive",
    21: "StartFormForbid",
    22: "Drop",
    23: "KitWaterPump",
    24: "FindChargerFailed",
    25: "LowPowerClean",
}


class RoidmiState(Enum):
    Unknown = -1
    Dormant = 1
    Idle = 2
    Paused = 3
    Sweeping = 4
    GoCharging = 5
    Charging = 6
    Error = 7
    Rfctrl = 8
    Fullcharge = 9
    Shutdown = 10
    FindChargerPause = 11


class RoidmiVacuumStatus(DeviceStatus):
    """Container for status reports from the vacuum."""

    def __init__(self, data):
        """
        Response (MIoT format) of a Roidme Eve Plus (roidmi.vacuum.v60)
        [
            {'did': 'battery_level', 'siid': 3, 'piid': 1},
            {'did': 'charging_state', 'siid': 3, 'piid': 2},
            {'did': 'error_code', 'siid': 2, 'piid': 2},
            {'did': 'state', 'siid': 2, 'piid': 1},
            {'did': 'filter_life_level', 'siid': 10, 'piid': 1},
            {'did': 'filter_left_minutes', 'siid': 10, 'piid': 2},
            {'did': 'main_brush_left_minutes', 'siid': 11, 'piid': 1},
            {'did': 'main_brush_life_level', 'siid': 11, 'piid': 2},
            {'did': 'side_brushes_left_minutes', 'siid': 12, 'piid': 1},
            {'did': 'side_brushes_life_level', 'siid': 12, 'piid': 2},
            {'did': 'sensor_dirty_time_left_minutes', 'siid': 15, 'piid': 1},
            {'did': 'sensor_dirty_remaning_level', 'siid': 15, 'piid': 2},
            {'did': 'sweep_mode', 'siid': 14, 'piid': 1},
            {'did': 'fanspeed_mode', 'siid': 2, 'piid': 4},
            {'did': 'sweep_type', 'siid': 2, 'piid': 8}
            {'did': 'path_mode', 'siid': 13, 'piid': 8},
            {'did': 'mop_present', 'siid': 8, 'piid': 1},
            {'did': 'work_station_freq', 'siid': 8, 'piid': 2},
            {'did': 'timing', 'siid': 8, 'piid': 6},
            {'did': 'clean_area', 'siid': 8, 'piid': 7},
            {'did': 'auto_boost', 'siid': 8, 'piid': 9},
            {'did': 'forbid_mode', 'siid': 8, 'piid': 10},
            {'did': 'water_level', 'siid': 8, 'piid': 11},
            {'did': 'total_clean_time_sec', 'siid': 8, 'piid': 13},
            {'did': 'total_clean_areas', 'siid': 8, 'piid': 14},
            {'did': 'clean_counts', 'siid': 8, 'piid': 18},
            {'did': 'clean_time_sec', 'siid': 8, 'piid': 19},
            {'did': 'double_clean', 'siid': 8, 'piid': 20},
            {'did': 'led_switch', 'siid': 8, 'piid': 22}
            {'did': 'lidar_collision', 'siid': 8, 'piid': 23},
            {'did': 'station_key', 'siid': 8, 'piid': 24},
            {'did': 'station_led', 'siid': 8, 'piid': 25},
            {'did': 'current_audio', 'siid': 8, 'piid': 26},
            {'did': 'station_type', 'siid': 8, 'piid': 29},
            {'did': 'volume', 'siid': 9, 'piid': 1},
            {'did': 'mute', 'siid': 9, 'piid': 2}
        ]

        """
        self.data = data

    @property
    def battery(self) -> int:
        """Remaining battery in percentage."""
        return self.data["battery_level"]

    @property
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    def error(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        try:
            return error_codes[self.error_code]
        except KeyError:
            return "Definition missing for error %s" % self.error_code

    @property
    def charging_state(self) -> ChargingState:
        """Charging state (Charging/Discharging)"""
        try:
            return ChargingState(self.data["charging_state"])
        except ValueError:
            _LOGGER.error("Unknown ChargingStats (%s)", self.data["charging_state"])
            return ChargingState.Unknown

    @property
    def sweep_mode(self) -> SweepMode:
        """Sweep mode point/area/total etc."""
        try:
            return SweepMode(self.data["sweep_mode"])
        except ValueError:
            _LOGGER.error("Unknown SweepMode (%s)", self.data["sweep_mode"])
            return SweepMode.Unknown

    @property
    def fan_speed(self) -> FanSpeed:
        """Current fan speed."""
        try:
            return FanSpeed(self.data["fanspeed_mode"])
        except ValueError:
            _LOGGER.error("Unknown FanSpeed (%s)", self.data["fanspeed_mode"])
            return FanSpeed.Unknown

    @property
    def sweep_type(self) -> SweepType:
        """Current sweep type sweep/mop/sweep&mop."""
        try:
            return SweepType(self.data["sweep_type"])
        except ValueError:
            _LOGGER.error("Unknown SweepType (%s)", self.data["sweep_type"])
            return SweepType.Unknown

    @property
    def path_mode(self) -> PathMode:
        """Current path-mode:  normal/y-mopping etc."""
        try:
            return PathMode(self.data["path_mode"])
        except ValueError:
            _LOGGER.error("Unknown PathMode (%s)", self.data["path_mode"])
            return PathMode.Unknown

    @property
    def is_mop_attached(self) -> bool:
        """Return True if mop is attached."""
        return self.data["mop_present"]

    @property
    def dust_collection_frequency(self) -> int:
        """Frequency for emptying the dust bin.

        Example: 2 means the dust bin is emptied every second cleaning.
        """
        return self.data["work_station_freq"]

    @property
    def timing(self) -> str:
        """Repeated cleaning
        Example: {"time":[[32400,1,3,0,[1,2,3,4,5],0,[12,10],null],[57600,0,1,2,[1,2,3,4,5,6,0],2,[],null]],"tz":2,"tzs":7200}
        Cleaning 1:
            32400 = startTime(9:00)
            1=Enabled
            3=FanSpeed.Strong
            0=SweepType.Sweep
            [1,2,3,4,5]=Monday-Friday
            0=WaterLevel
            [12,10]=List of rooms
            null: ?Might be related to "Customize"?
        Cleaning 2:
            57600 = startTime(16:00)
            0=Disabled
            1=FanSpeed.Silent
            2=SweepType.MopAndSweep
            [1,2,3,4,5,6,0]=Monday-Sunday
            2=WaterLevel.Second
            []=All rooms
            null: ?Might be related to "Customize"?
        tz/tzs= time-zone
        """
        return self.data["timing"]

    @property
    def carpet_mode(self) -> bool:
        """Auto boost on carpet."""
        return self.data["auto_boost"]

    def _parse_forbid_mode(self, val) -> DNDStatus:
        # Example data: {"time":[75600,21600,1],"tz":2,"tzs":7200}
        def _seconds_to_components(val):
            hour = math.floor(val / 3600)
            minut = math.floor((val - hour * 3600) / 60)
            return (hour, minut)

        as_dict = json.loads(val)
        enabled = bool(as_dict["time"][2])
        start = _seconds_to_components(as_dict["time"][0])
        end = _seconds_to_components(as_dict["time"][1])
        return DNDStatus(
            dict(
                enabled=enabled,
                start_hour=start[0],
                start_minute=start[1],
                end_hour=end[0],
                end_minute=end[1],
            )
        )

    @property
    def dnd_status(self) -> DNDStatus:
        """Returns do-not-disturb status."""
        return self._parse_forbid_mode(self.data["forbid_mode"])

    @property
    def water_level(self) -> WaterLevel:
        """Get current water level."""
        try:
            return WaterLevel(self.data["water_level"])
        except ValueError:
            _LOGGER.error("Unknown WaterLevel (%s)", self.data["water_level"])
            return WaterLevel.Unknown

    @property
    def double_clean(self) -> bool:
        """Is double clean enabled."""
        return self.data["double_clean"]

    @property
    def led(self) -> bool:
        """Return True if led/display on vaccum is on."""
        return self.data["led_switch"]

    @property
    def is_lidar_collision_sensor(self) -> bool:
        """When ON, the robot will use lidar as the main detection sensor to help reduce
        collisions."""
        return self.data["lidar_collision"]

    @property
    def station_key(self) -> bool:
        """When ON: long press the display will turn on dust collection."""
        return self.data["station_key"]

    @property
    def station_led(self) -> bool:
        """Return if station display is on."""
        return self.data["station_led"]

    @property
    def current_audio(self) -> str:
        """Current voice setting.

        E.g. 'girl_en'
        """
        return self.data["current_audio"]

    @property
    def clean_time(self) -> timedelta:
        """Time used for cleaning (if finished, shows how long it took)."""
        return timedelta(seconds=self.data["clean_time_sec"])

    @property
    def clean_area(self) -> int:
        """Cleaned area in m2."""
        return self.data["clean_area"]

    @property
    def state_code(self) -> int:
        """State code as returned by the device."""
        return int(self.data["state"])

    @property
    def state(self) -> RoidmiState:
        """Human readable state description, see also :func:`state_code`."""
        try:
            return RoidmiState(self.state_code)
        except ValueError:
            _LOGGER.error("Unknown RoidmiState (%s)", self.state_code)
            return RoidmiState.Unknown

    @property
    def volume(self) -> int:
        """Return device sound volumen level."""
        return self.data["volume"]

    @property
    def is_muted(self) -> bool:
        """True if device is muted."""
        return bool(self.data["mute"])

    @property
    def is_paused(self) -> bool:
        """Return True if vacuum is paused."""
        return self.state in [RoidmiState.Paused, RoidmiState.FindChargerPause]

    @property
    def is_on(self) -> bool:
        """True if device is currently cleaning in any mode."""
        return self.state == RoidmiState.Sweeping

    @property
    def got_error(self) -> bool:
        """True if an error has occured."""
        return self.error_code != 0


class RoidmiCleaningSummary(DeviceStatus):
    """Contains summarized information about available cleaning runs."""

    def __init__(self, data) -> None:
        self.data = data

    @property
    def total_duration(self) -> timedelta:
        """Total cleaning duration."""
        return timedelta(seconds=self.data["total_clean_time_sec"])

    @property
    def total_area(self) -> int:
        """Total cleaned area."""
        return self.data["total_clean_areas"]

    @property
    def count(self) -> int:
        """Number of cleaning runs."""
        return self.data["clean_counts"]


class RoidmiConsumableStatus(DeviceStatus):
    """Container for consumable status information, including information about brushes
    and duration until they should be changed.

    The methods returning time left are based values returned from the device.
    """

    def __init__(self, data):
        self.data = data

    def _calcUsageTime(
        self, renaning_time: timedelta, remaning_level: int
    ) -> timedelta:
        remaning_fraction = remaning_level / 100.0
        original_total = renaning_time / remaning_fraction
        return original_total * (1 - remaning_fraction)

    @property
    def filter(self) -> timedelta:
        """Filter usage time."""
        return self._calcUsageTime(self.filter_left, self.data["filter_life_level"])

    @property
    def filter_left(self) -> timedelta:
        """How long until the filter should be changed."""
        return timedelta(minutes=self.data["filter_left_minutes"])

    @property
    def main_brush(self) -> timedelta:
        """Main brush usage time."""
        return self._calcUsageTime(
            self.main_brush_left, self.data["main_brush_life_level"]
        )

    @property
    def main_brush_left(self) -> timedelta:
        """How long until the main brush should be changed."""
        return timedelta(minutes=self.data["main_brush_left_minutes"])

    @property
    def side_brush(self) -> timedelta:
        """Main brush usage time."""
        return self._calcUsageTime(
            self.side_brush_left, self.data["side_brushes_life_level"]
        )

    @property
    def side_brush_left(self) -> timedelta:
        """How long until the side brushes should be changed."""
        return timedelta(minutes=self.data["side_brushes_left_minutes"])

    @property
    def sensor_dirty(self) -> timedelta:
        """Return time since last sensor clean."""
        return self._calcUsageTime(
            self.sensor_dirty_left, self.data["sensor_dirty_remaning_level"]
        )

    @property
    def sensor_dirty_left(self) -> timedelta:
        """How long until the sensors should be cleaned."""
        return timedelta(minutes=self.data["sensor_dirty_time_left_minutes"])


class RoidmiVacuumMiot(MiotDevice):
    """Interface for Vacuum Eve Plus (roidmi.vacuum.v60)"""

    mapping = _MAPPING

    @command()
    def status(self) -> RoidmiVacuumStatus:
        """State of the vacuum."""
        return RoidmiVacuumStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                # max_properties limmit to 10 to avoid "Checksum error" messages from the device.
                for prop in self.get_properties_for_mapping()
            }
        )

    @command()
    def consumable_status(self) -> RoidmiConsumableStatus:
        """Return information about consumables."""
        return RoidmiConsumableStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                # max_properties limmit to 10 to avoid "Checksum error" messages from the device.
                for prop in self.get_properties_for_mapping()
            }
        )

    @command()
    def cleaning_summary(self) -> RoidmiCleaningSummary:
        """Return information about cleaning runs."""
        return RoidmiCleaningSummary(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                # max_properties limmit to 10 to avoid "Checksum error" messages from the device.
                for prop in self.get_properties_for_mapping()
            }
        )

    @command()
    def start(self) -> None:
        """Start cleaning."""
        return self.call_action("start")

    # @command(click.argument("roomstr", type=str, required=False))
    # def start_room_sweep_unknown(self, roomstr: str=None) -> None:
    #     """Start room cleaning.

    #     roomstr: empty means start room clean of all rooms. FIXME: the syntax of an non-empty roomstr is still unknown
    #     """
    #     return self.call_action("start_room_sweep", roomstr)

    # @command(
    # click.argument("sweep_mode", type=EnumType(SweepMode)),
    # click.argument("clean_info", type=str),
    # )
    # def start_sweep_unknown(self, sweep_mode: SweepMode, clean_info: str=None) -> None:
    #     """Start sweep with mode.

    #     FIXME: the syntax of start_sweep is unknown
    #     """
    #     return self.call_action("start_sweep", [sweep_mode.value, clean_info])

    @command()
    def stop(self) -> None:
        """Stop cleaning."""
        return self.call_action("stop")

    @command()
    def home(self) -> None:
        """Return to home."""
        return self.call_action("home")

    @command()
    def identify(self) -> None:
        """Locate the device (i am here)."""
        return self.call_action("identify")

    @command(click.argument("on", type=bool))
    def set_station_led(self, on: bool):
        """Enable station led display."""
        return self.set_property("station_led", on)

    @command(click.argument("on", type=bool))
    def set_led(self, on: bool):
        """Enable vacuum led."""
        return self.set_property("led_switch", on)

    @command(click.argument("vol", type=int))
    def set_sound_volume(self, vol: int):
        """Set sound volume [0-100]."""
        return self.set_property("volume", vol)

    @command(click.argument("value", type=bool))
    def set_sound_muted(self, value: bool):
        """Set sound volume muted."""
        return self.set_property("mute", value)

    @command(click.argument("fanspeed_mode", type=EnumType(FanSpeed)))
    def set_fanspeed(self, fanspeed_mode: FanSpeed):
        """Set fan speed."""
        return self.set_property("fanspeed_mode", fanspeed_mode.value)

    @command(click.argument("sweep_type", type=EnumType(SweepType)))
    def set_sweep_type(self, sweep_type: SweepType):
        """Set sweep_type."""
        return self.set_property("sweep_type", sweep_type.value)

    @command(click.argument("path_mode", type=EnumType(PathMode)))
    def set_path_mode(self, path_mode: PathMode):
        """Set path_mode."""
        return self.set_property("path_mode", path_mode.value)

    @command(click.argument("dust_collection_frequency", type=int))
    def set_dust_collection_frequency(self, dust_collection_frequency: int):
        """Set frequency for emptying the dust bin.

        Example: 2 means the dust bin is emptied every second cleaning.
        """
        return self.set_property("work_station_freq", dust_collection_frequency)

    @command(click.argument("timing", type=str))
    def set_timing(self, timing: str):
        """Set repeated clean timing.

        Set timing to 9:00 Monday-Friday, rooms:[12,10]
        timing = '{"time":[[32400,1,3,0,[1,2,3,4,5],0,[12,10],null]],"tz":2,"tzs":7200}'
        See also :func:`RoidmiVacuumStatus.timing`

        NOTE: setting timing will override existing settings
        """
        return self.set_property("timing", timing)

    @command(click.argument("auto_boost", type=bool))
    def set_carpet_mode(self, auto_boost: bool):
        """Set auto boost on carpet."""
        return self.set_property("auto_boost", auto_boost)

    def _set_dnd(self, start_int: int, end_int: int, active: bool):
        value_str = json.dumps({"time": [start_int, end_int, int(active)]})
        return self.set_property("forbid_mode", value_str)

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
        start_int = int(timedelta(hours=start_hr, minutes=start_min).total_seconds())
        end_int = int(timedelta(hours=end_hr, minutes=end_min).total_seconds())
        return self._set_dnd(start_int, end_int, active=True)

    @command()
    def disable_dnd(self):
        """Disable do-not-disturb."""
        # The current do not disturb is read back for a better user expierence,
        # as start/end time must be set together with enabled=False
        try:
            current_dnd_str = self.get_property_by(**_MAPPING["forbid_mode"])[0][
                "value"
            ]
            current_dnd_dict = json.loads(current_dnd_str)
        except Exception:
            # In case reading current DND back fails, DND is disabled anyway
            return self._set_dnd(0, 0, active=False)
        return self._set_dnd(
            current_dnd_dict["time"][0], current_dnd_dict["time"][1], active=False
        )

    @command(click.argument("water_level", type=EnumType(WaterLevel)))
    def set_water_level(self, water_level: WaterLevel):
        """Set water_level."""
        return self.set_property("water_level", water_level.value)

    @command(click.argument("double_clean", type=bool))
    def set_double_clean(self, double_clean: bool):
        """Set double clean (True/False)."""
        return self.set_property("double_clean", double_clean)

    @command(click.argument("lidar_collision", type=bool))
    def set_lidar_collision_sensor(self, lidar_collision: bool):
        """When ON, the robot will use lidar as the main detection sensor to help reduce
        collisions."""
        return self.set_property("lidar_collision", lidar_collision)

    @command()
    def start_dust(self) -> None:
        """Start base dust collection."""
        return self.call_action("start_station_dust_collection")

    # @command(click.argument("voice", type=str))
    #     def set_voice_unknown(self, voice: str) -> None:
    #     """Set voice.

    #     FIXME: the syntax of voice is unknown (assumed to be json format)
    #     """
    #     return self.call_action("set_voice", voice)

    @command()
    def reset_filter_life(self) -> None:
        """Reset filter life."""
        return self.call_action("reset_filter_life")

    @command()
    def reset_mainbrush_life(self) -> None:
        """Reset main brush life."""
        return self.call_action("reset_main_brush_life")

    @command()
    def reset_sidebrush_life(self) -> None:
        """Reset side brushes life."""
        return self.call_action("reset_side_brushes_life")

    @command()
    def reset_sensor_dirty_life(self) -> None:
        """Reset sensor dirty life."""
        return self.call_action("reset_sensor_dirty_life")
