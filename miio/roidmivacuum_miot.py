"""Vacuum Eve Plus (roidmi.vacuum.v60)"""

# https://github.com/rytilahti/python-miio/issues/543#issuecomment-755767331

import json
import logging
import math
from enum import Enum

import click

from .click_common import EnumType, command, format_output
from .miot_device import DeviceStatus as DeviceStatusContainer
from .miot_device import MiotDevice, MiotMapping

_LOGGER = logging.getLogger(__name__)

_MAPPING: MiotMapping = {
    "battery_level": {"siid": 3, "piid": 1},
    "charging_state": {"siid": 3, "piid": 2},
    "device_fault": {"siid": 2, "piid": 2},
    "device_status": {"siid": 2, "piid": 1},
    "filter_life_level": {"siid": 10, "piid": 1},
    "filter_left_time": {"siid": 10, "piid": 2},
    "brush_left_time": {"siid": 11, "piid": 1},
    "brush_life_level": {"siid": 11, "piid": 2},
    "brush_left_time2": {"siid": 12, "piid": 1},
    "brush_life_level2": {"siid": 12, "piid": 2},
    "brush_left_time3": {"siid": 15, "piid": 1},
    "brush_life_level3": {"siid": 15, "piid": 2},
    "sweep_mode": {"siid": 14, "piid": 1},
    "cleaning_mode": {"siid": 2, "piid": 4},
    "sweep_type": {"siid": 2, "piid": 8},
    "path_mode": {"siid": 13, "piid": 8},
    "mop_present": {"siid": 8, "piid": 1},
    "work_station_freq": {"siid": 8, "piid": 2},  # Range: [0, 3, 1]
    "timing": {"siid": 8, "piid": 6},  # str (example: {"tz":2,"tzs":7200})
    "clean_area": {"siid": 8, "piid": 7},  # uint32
    # "uid": {"siid": 8, "piid": 8}, # str
    "auto_boost": {"siid": 8, "piid": 9},  # bool (auto boost on carpet)
    "forbid_mode": {"siid": 8, "piid": 10},  # str
    "water_level": {"siid": 8, "piid": 11},
    # "siid8_13": {"siid": 8, "piid": 13}, # no-name: (uint32, unit: seconds) (acc: ['read', 'notify'])
    # "siid8_14": {"siid": 8, "piid": 14}, # no-name: (uint32, unit: none) (acc: ['read', 'notify'])
    "clean_counts": {"siid": 8, "piid": 18},
    # "siid8_19": {"siid": 8, "piid": 19}, # no-name: (uint32, unit: seconds) (acc: ['read', 'notify'])
    "double_clean": {"siid": 8, "piid": 20},
    "edge_sweep": {"siid": 8, "piid": 21},
    "led_switch": {"siid": 8, "piid": 22},
    "lidar_collision": {"siid": 8, "piid": 23},
    "station_key": {"siid": 8, "piid": 24},
    "station_led": {"siid": 8, "piid": 25},
    "current_audio": {"siid": 8, "piid": 26},  # str (example: girl_en)
    "progress": {"siid": 8, "piid": 28},
    # "station_type": {"siid": 8, "piid": 29}, # uint32
    # "voice_conf": {"siid": 8, "piid": 30},
    # "switch_status": {"siid": 2, "piid": 10},
    "volume": {"siid": 9, "piid": 1},
    "mute": {"siid": 9, "piid": 2},
}


class ChargingState(Enum):
    Unknown = -1
    Charging = 1
    Discharging = 2
    NotChargeable = 4


class CleaningMode(Enum):
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


class SwitchStatus(Enum):
    Unknown = -1
    Open = 1


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


class FaultStatus(Enum):
    Unknown = -1
    NoFaults = 0
    LowBatteryFindCharger = 1
    LowBatteryAndPoweroff = 2
    WheelRap = 3
    CollisionError = 4
    TileDoTask = 5
    LidarPointError = 6
    FrontWallError = 7
    PsdDirty = 8
    MiddleBrushFatal = 9
    SidBrush = 10
    FanSpeedError = 11
    LidarCover = 12
    GarbageBoxFull = 13
    GarbageBoxOut = 14
    GarbageBoxFullOut = 15
    PhysicalTrapped = 16
    PickUpDoTask = 17
    NoWaterBoxDoTask = 18
    WaterBoxEmpty = 19
    CleanCannotArrive = 20
    StartFormForbid = 21
    Drop = 22
    KitWaterPump = 23
    FindChargerFailed = 24
    LowPowerClean = 25


class DeviceStatus(Enum):
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


class RoidmiVacuumStatus(DeviceStatusContainer):
    def __init__(self, data):
        self.data = data

    @property
    def battery_level(self) -> int:
        return self.data["battery_level"]

    @property
    def filter_left_time(self) -> int:
        return self.data["filter_left_time"]

    @property
    def filter_life_level(self) -> int:
        return self.data["filter_life_level"]

    @property
    def brush_left_time(self) -> int:
        return self.data["brush_left_time"]

    @property
    def brush_life_level(self) -> int:
        return self.data["brush_life_level"]

    @property
    def brush_left_time2(self) -> int:
        return self.data["brush_left_time2"]

    @property
    def brush_life_level2(self) -> int:
        return self.data["brush_life_level2"]

    @property
    def brush_left_time3(self) -> int:
        return self.data["brush_left_time3"]

    @property
    def brush_life_level3(self) -> int:
        return self.data["brush_life_level3"]

    @property
    def device_fault(self) -> FaultStatus:
        try:
            return FaultStatus(self.data["device_fault"])
        except ValueError:
            _LOGGER.error("Unknown FaultStatus (%s)", self.data["device_fault"])
            return FaultStatus.Unknown

    @property
    def charging_state(self) -> ChargingState:
        try:
            return ChargingState(self.data["charging_state"])
        except ValueError:
            _LOGGER.error("Unknown ChargingStats (%s)", self.data["charging_state"])
            return ChargingState.Unknown

    @property
    def sweep_mode(self) -> SweepMode:
        try:
            return SweepMode(self.data["sweep_mode"])
        except ValueError:
            _LOGGER.error("Unknown SweepMode (%s)", self.data["sweep_mode"])
            return SweepMode.Unknown

    @property
    def cleaning_mode(self) -> CleaningMode:
        try:
            return CleaningMode(self.data["cleaning_mode"])
        except ValueError:
            _LOGGER.error("Unknown CleaningMode (%s)", self.data["cleaning_mode"])
            return CleaningMode.Unknown

    @property
    def sweep_type(self) -> SweepType:
        try:
            return SweepType(self.data["sweep_type"])
        except ValueError:
            _LOGGER.error("Unknown SweepType (%s)", self.data["sweep_type"])
            return SweepType.Unknown

    @property
    def path_mode(self) -> PathMode:
        try:
            return PathMode(self.data["path_mode"])
        except ValueError:
            _LOGGER.error("Unknown PathMode (%s)", self.data["path_mode"])
            return PathMode.Unknown

    @property
    def mop_present(self) -> bool:
        return self.data["mop_present"]

    @property
    def work_station_freq(self) -> int:
        return self.data["work_station_freq"]

    @property
    def timing(self) -> str:
        return self.data["timing"]

    @property
    def clean_area(self) -> int:
        return self.data["clean_area"]

    @property
    def uid(self) -> int:
        return self.data["uid"]

    @property
    def auto_boost(self) -> int:
        return self.data["auto_boost"]

    def parseForbidMode(self, val):
        def secToClock(val):
            hour = math.floor(val / 3600)
            minut = math.floor((val - hour * 3600) / 60)
            return "{}:{:02}".format(hour, minut)

        asDict = json.loads(val)
        active = bool(asDict["time"][2])
        begin = secToClock(asDict["time"][0])
        end = secToClock(asDict["time"][1])
        return json.dumps(
            {"enabled": active, "begin": begin, "end": end, "tz": asDict["tz"]}
        )

    @property
    def forbid_mode(self) -> int:
        # Example data: {"time":[75600,21600,1],"tz":2,"tzs":7200}
        return self.parseForbidMode(self.data["forbid_mode"])

    @property
    def water_level(self) -> WaterLevel:
        try:
            return WaterLevel(self.data["water_level"])
        except ValueError:
            _LOGGER.error("Unknown WaterLevel (%s)", self.data["water_level"])
            return WaterLevel.Unknown

    # @property
    # def siid8_13(self) -> int:
    #     return self.data["siid8_13"]

    # @property
    # def siid8_14(self) -> int:
    #     return self.data["siid8_14"]

    @property
    def clean_counts(self) -> int:
        return self.data["clean_counts"]

    # @property
    # def siid8_19(self) -> int:
    #     return self.data["siid8_19"]

    @property
    def double_clean(self) -> bool:
        return self.data["double_clean"]

    @property
    def edge_sweep(self) -> bool:
        return self.data["edge_sweep"]

    @property
    def led_switch(self) -> bool:
        return self.data["led_switch"]

    @property
    def lidar_collision(self) -> bool:
        return self.data["lidar_collision"]

    @property
    def station_key(self) -> bool:
        return self.data["station_key"]

    @property
    def station_led(self) -> bool:
        return self.data["station_led"]

    @property
    def current_audio(self) -> str:
        return self.data["current_audio"]

    @property
    def progress(self) -> str:
        return self.data["progress"]

    @property
    def voice_conf(self) -> str:
        return self.data["voice_conf"]

    @property
    def switch_status(self) -> SwitchStatus:
        try:
            return SwitchStatus(self.data["switch_status"])
        except TypeError:
            _LOGGER.error("Unknown SwitchStatus (%s)", self.data["switch_status"])
            return SwitchStatus.Unknown

    @property
    def device_status(self) -> DeviceStatus:
        try:
            return DeviceStatus(self.data["device_status"])
        except TypeError:
            _LOGGER.error("Unknown DeviceStatus (%s)", self.data["device_status"])
            return DeviceStatus.Unknown

    @property
    def volume(self) -> int:
        return self.data["volume"]

    @property
    def mute(self) -> bool:
        return self.data["mute"]


class RoidmiVacuumMiot(MiotDevice):
    """Interface for Vacuum Eve Plus (roidmi.vacuum.v60)"""

    mapping = _MAPPING

    @command(
        default_output=format_output(
            "\n",
            "Battery level: {result.battery_level}\n"
            "Brush life level: {result.brush_life_level}\n"
            "Brush left time: {result.brush_left_time}\n"
            "Charging state: {result.charging_state.name}\n"
            "Device fault: {result.device_fault.name}\n"
            "Device status: {result.device_status.name}\n"
            "Filter left level: {result.filter_left_time}\n"
            "Filter life level: {result.filter_life_level}\n"
            "Operating mode: {result.sweep_mode.name}\n"
            "Right side cleaning brush left time: {result.brush_left_time2}\n"
            "Right side cleaning brush life level: {result.brush_life_level2}\n"
            "Left side cleaning brush left time: {result.brush_left_time3}\n"
            "Left side cleaning brush life level: {result.brush_life_level3}\n"
            "Cleaning mode: {result.cleaning_mode.name}\n"
            "Sweep type: {result.sweep_type.name}\n"
            "Path mode: {result.path_mode.name}\n"
            "Sweep mode: {result.sweep_mode.name}\n"
            "Mop present: {result.mop_present}\n"
            "work_station_freq: {result.work_station_freq}\n"
            "timing: {result.timing}\n"
            "clean_area: {result.clean_area}\n"
            # "uid: {result.uid}\n"
            "auto_boost: {result.auto_boost}\n"
            "forbid_mode: {result.forbid_mode}\n"
            "Water level: {result.water_level.name}\n"
            # "Unknown siid8_13 [sec]: {result.siid8_13}\n"
            # "Unknown siid8_14 [uint32]: {result.siid8_14}\n"
            "clean_counts: {result.clean_counts}\n"
            # "Unknown siid8_19 [sec]: {result.siid8_19}\n"
            "Double clean: {result.double_clean}\n"
            "Edge sweep: {result.edge_sweep}\n"
            "Led switch: {result.led_switch}\n"
            "Lidar collision: {result.lidar_collision}\n"
            "Station key: {result.station_key}\n"
            "Station led: {result.station_led}\n"
            "Current audio: {result.current_audio}\n"
            "Progress: {result.progress}\n"
            # "Voice config: {result.voice_conf}\n"
            # "Switch status: {result.switch_status.name}\n"
            "Volume: {result.volume}\n" "Mute: {result.mute}\n",
        )
    )
    def status(self) -> RoidmiVacuumStatus:
        """State of the vacuum."""

        return RoidmiVacuumStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                # max_properties limmit to 10 to avoid "Checksum error" messages from the device.
                for prop in self.get_properties_for_mapping(max_properties=10)
            }
        )

    @command()
    def start(self) -> None:
        """Start cleaning."""
        return self.call_action_by(2, 1)

    @command(click.argument("roomstr", type=str))
    def start_room_sweep_unknown(self, roomstr: str) -> None:
        """Start cleaning.

        FIXME: the syntax of voice is unknown
        """
        return self.call_action_by(2, 3, roomstr)

    @command(
        click.argument("sweep_mode", type=EnumType(SweepMode)),
        click.argument("clean_info", type=str),
    )
    def start_sweep_unknown(self, sweep_mode: SweepMode, clean_info: str) -> None:
        """Start sweep with mode.

        FIXME: the syntax of start sweep with mode is unknown
        """
        return self.call_action_by(14, 1, [sweep_mode.value, clean_info])

    @command()
    def stop(self) -> None:
        """Stop cleaning."""
        return self.call_action_by(2, 2)

    @command()
    def home(self) -> None:
        """Return to home."""
        return self.call_action_by(3, 1)

    @command()
    def identify(self) -> None:
        """Locate the device (i am here)."""
        return self.call_action_by(8, 1)

    @command(click.argument("vol", type=int))
    def set_sound_volume(self, vol: int):
        """Set sound volume [0-100]."""
        return self.set_property("volume", vol)

    @command(click.argument("cleaning_mode", type=EnumType(CleaningMode)))
    def set_cleaning_mode(self, cleaning_mode: CleaningMode):
        """Set cleaning_mode."""
        return self.set_property("cleaning_mode", cleaning_mode.value)

    @command(click.argument("sweep_type", type=EnumType(SweepType)))
    def set_sweep_type(self, sweep_type: SweepType):
        """Set sweep_type."""
        return self.set_property("sweep_type", sweep_type.value)

    @command(click.argument("path_mode", type=EnumType(PathMode)))
    def set_path_mode(self, path_mode: PathMode):
        """Set path_mode."""
        return self.set_property("path_mode", path_mode.value)

    @command(click.argument("work_station_freq", type=int))
    def set_work_station_freq(self, work_station_freq: int):
        """Set work_station_freq (2 means Auto dust colect every second time)."""
        return self.set_property("work_station_freq", work_station_freq)

    @command(click.argument("timing", type=str))
    def set_timing_unknown(self, timing: str):
        """Set time zone.

        FIXME: the syntax of timing is unknown
        """
        return self.set_property("timing", timing)

    @command(click.argument("auto_boost", type=bool))
    def set_auto_boost(self, auto_boost: bool):
        """Set auto boost on carpet."""
        return self.set_property("auto_boost", auto_boost)

    @command(
        click.argument("begin", type=str),
        click.argument("end", type=str),
        click.argument("active", type=bool, required=False, default=True),
    )
    def set_forbid_mode(self, begin: str, end: str, active: bool = True):
        """Set do not disturbe.

        E.g. begin="22:00" end="05:00"
        """

        def clockToSec(clock):
            hour, minut = clock.split(":")
            return int(hour) * 3600 + int(minut) * 60

        begin_int = clockToSec(begin)
        end_int = clockToSec(end)
        value_str = json.dumps({"time": [begin_int, end_int, int(active)]})
        return self.set_property("forbid_mode", value_str)

    @command(click.argument("water_level", type=EnumType(WaterLevel)))
    def set_water_level(self, water_level: WaterLevel):
        """Set water_level."""
        return self.set_property("water_level", water_level.value)

    @command(click.argument("double_clean", type=bool))
    def set_double_clean(self, double_clean: bool):
        """Set double clean (True/False)."""
        return self.set_property("double_clean", double_clean)

    @command(click.argument("edge_sweep", type=bool))
    def set_edge_sweep(self, edge_sweep: bool):
        """Set edge_sweep (True/False)."""
        return self.set_property("edge_sweep", edge_sweep)

    @command(click.argument("lidar_collision", type=bool))
    def set_lidar_collision(self, lidar_collision: bool):
        """Set lidar collision (True/False).."""
        return self.set_property("lidar_collision", lidar_collision)

    @command()
    def start_dust(self) -> None:
        """Start base dust collection."""
        return self.call_action_by(8, 6)

    @command(click.argument("voice", type=str))
    def set_voice_unknown(self, voice: str) -> None:
        """Set voice.

        FIXME: the syntax of voice is unknown
        """
        return self.call_action_by(8, 12, voice)

    @command()
    def reset_filter_life(self) -> None:
        """Reset filter life."""
        return self.call_action_by(10, 1)

    @command()
    def reset_mainbrush_life(self) -> None:
        """Reset main brush life."""
        return self.call_action_by(11, 1)

    @command()
    def reset_sidebrush_life(self) -> None:
        """Reset side brush life."""
        return self.call_action_by(12, 1)

    @command()
    def reset_sidebrush_left_life(self) -> None:
        """Reset side brush life."""
        return self.call_action_by(15, 1)
