"""Dreame Vacuum."""

import logging
from enum import Enum
from typing import Dict

import click

from miio.click_common import command, format_output
from miio.exceptions import DeviceException
from miio.miot_device import DeviceStatus as DeviceStatusContainer
from miio.miot_device import MiotDevice, MiotMapping
from miio.utils import deprecated

_LOGGER = logging.getLogger(__name__)


DREAME_1C = "dreame.vacuum.mc1808"
DREAME_F9 = "dreame.vacuum.p2008"

MIOT_MAPPING: Dict[str, MiotMapping] = {
    DREAME_1C: {
        # https://home.miot-spec.com/spec/dreame.vacuum.mc1808
        "battery_level": {"siid": 2, "piid": 1},
        "charging_state": {"siid": 2, "piid": 2},
        "device_fault": {"siid": 3, "piid": 1},
        "device_status": {"siid": 3, "piid": 2},
        "brush_left_time": {"siid": 26, "piid": 1},
        "brush_life_level": {"siid": 26, "piid": 2},
        "filter_life_level": {"siid": 27, "piid": 1},
        "filter_left_time": {"siid": 27, "piid": 2},
        "brush_left_time2": {"siid": 28, "piid": 1},
        "brush_life_level2": {"siid": 28, "piid": 2},
        "operating_mode": {"siid": 18, "piid": 1},
        "cleaning_mode": {"siid": 18, "piid": 6},
        "delete_timer": {"siid": 18, "piid": 8},
        "cleaning_time": {"siid": 18, "piid": 2},
        "cleaning_area": {"siid": 18, "piid": 4},
        "first_clean_time": {"siid": 18, "piid": 12},
        "total_clean_time": {"siid": 18, "piid": 13},
        "total_clean_times": {"siid": 18, "piid": 14},
        "total_clean_area": {"siid": 18, "piid": 15},
        "life_sieve": {"siid": 19, "piid": 1},
        "life_brush_side": {"siid": 19, "piid": 2},
        "life_brush_main": {"siid": 19, "piid": 3},
        "timer_enable": {"siid": 20, "piid": 1},
        "start_time": {"siid": 20, "piid": 2},
        "stop_time": {"siid": 20, "piid": 3},
        "deg": {"siid": 21, "piid": 1, "access": ["write"]},
        "speed": {"siid": 21, "piid": 2, "access": ["write"]},
        "map_view": {"siid": 23, "piid": 1},
        "frame_info": {"siid": 23, "piid": 2},
        "volume": {"siid": 24, "piid": 1},
        "voice_package": {"siid": 24, "piid": 3},
        "timezone": {"siid": 25, "piid": 1},
        "home": {"siid": 2, "aiid": 1},
        "locate": {"siid": 17, "aiid": 1},
        "start_clean": {"siid": 3, "aiid": 1},
        "stop_clean": {"siid": 3, "aiid": 2},
        "reset_mainbrush_life": {"siid": 26, "aiid": 1},
        "reset_filter_life": {"siid": 27, "aiid": 1},
        "reset_sidebrush_life": {"siid": 28, "aiid": 1},
        "move": {"siid": 21, "aiid": 1},
        "play_sound": {"siid": 24, "aiid": 3},
    },
    DREAME_F9: {
        # https://home.miot-spec.com/spec/dreame.vacuum.p2008
        "battery_level": {"siid": 3, "piid": 1},
        "charging_state": {"siid": 3, "piid": 2},
        "device_fault": {"siid": 2, "piid": 2},
        "device_status": {"siid": 2, "piid": 1},
        "brush_left_time": {"siid": 9, "piid": 1},
        "brush_life_level": {"siid": 9, "piid": 2},
        "filter_life_level": {"siid": 11, "piid": 1},
        "filter_left_time": {"siid": 11, "piid": 2},
        "brush_left_time2": {"siid": 10, "piid": 1},
        "brush_life_level2": {"siid": 10, "piid": 2},
        "operating_mode": {"siid": 4, "piid": 1},
        "cleaning_mode": {"siid": 4, "piid": 4},
        "delete_timer": {"siid": 18, "piid": 8},
        "timer_enable": {"siid": 5, "piid": 1},
        "cleaning_time": {"siid": 4, "piid": 2},
        "cleaning_area": {"siid": 4, "piid": 3},
        "first_clean_time": {"siid": 12, "piid": 1},
        "total_clean_time": {"siid": 12, "piid": 2},
        "total_clean_times": {"siid": 12, "piid": 3},
        "total_clean_area": {"siid": 12, "piid": 4},
        "start_time": {"siid": 5, "piid": 2},
        "stop_time": {"siid": 5, "piid": 3},
        "map_view": {"siid": 6, "piid": 1},
        "frame_info": {"siid": 6, "piid": 2},
        "volume": {"siid": 7, "piid": 1},
        "voice_package": {"siid": 7, "piid": 2},
        "water_flow": {"siid": 4, "piid": 5},
        "water_tank_status": {"siid": 4, "piid": 6},
        "timezone": {"siid": 8, "piid": 1},
        "home": {"siid": 3, "aiid": 1},
        "locate": {"siid": 7, "aiid": 1},
        "start_clean": {"siid": 4, "aiid": 1},
        "stop_clean": {"siid": 4, "aiid": 2},
        "reset_mainbrush_life": {"siid": 9, "aiid": 1},
        "reset_filter_life": {"siid": 11, "aiid": 1},
        "reset_sidebrush_life": {"siid": 10, "aiid": 1},
        "move": {"siid": 21, "aiid": 1},
        "play_sound": {"siid": 7, "aiid": 2},
    },
}


class ChargingState(Enum):
    Unknown = -1
    Charging = 1
    Discharging = 2
    Charging2 = 4
    GoCharging = 5


class CleaningModeDreame1C(Enum):
    Unknown = -1
    Quiet = 0
    Default = 1
    Medium = 2
    Strong = 3


class CleaningModeDreameF9(Enum):
    Unknown = -1
    Quiet = 0
    Standart = 1
    Strong = 2
    Turbo = 3


class OperatingMode(Enum):
    Unknown = -1
    Paused = 1
    Cleaning = 2
    GoCharging = 3
    Charging = 6
    ManualCleaning = 13
    Sleeping = 14
    ManualPaused = 17
    ZonedCleaning = 19


class FaultStatus(Enum):
    Unknown = -1
    NoFaults = 0


class DeviceStatus(Enum):
    Unknown = -1
    Sweeping = 1
    Idle = 2
    Paused = 3
    Error = 4
    GoCharging = 5
    Charging = 6
    ManualSweeping = 13


class WaterFlow(Enum):
    Unknown = -1
    Low = 1
    Medium = 2
    High = 3


class WaterTankStatus(Enum):
    Unknown = -1
    NotAttached = 0
    Attached = 1


class DreameVacuumStatusBase(DeviceStatusContainer):
    def __init__(self, data):
        self.data = data

    @property
    def battery_level(self) -> str:
        return self.data["battery_level"]

    @property
    def brush_left_time(self) -> str:
        return self.data["brush_left_time"]

    @property
    def brush_left_time2(self) -> str:
        return self.data["brush_left_time2"]

    @property
    def brush_life_level2(self) -> str:
        return self.data["brush_life_level2"]

    @property
    def brush_life_level(self) -> str:
        return self.data["brush_life_level"]

    @property
    def filter_left_time(self) -> str:
        return self.data["filter_left_time"]

    @property
    def filter_life_level(self) -> str:
        return self.data["filter_life_level"]

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
    def operating_mode(self) -> OperatingMode:
        try:
            return OperatingMode(self.data["operating_mode"])
        except ValueError:
            _LOGGER.error("Unknown OperatingMode (%s)", self.data["operating_mode"])
            return OperatingMode.Unknown

    @property
    def device_status(self) -> DeviceStatus:
        try:
            return DeviceStatus(self.data["device_status"])
        except TypeError:
            _LOGGER.error("Unknown DeviceStatus (%s)", self.data["device_status"])
            return DeviceStatus.Unknown

    @property
    def timer_enable(self) -> str:
        return self.data["timer_enable"]

    @property
    def start_time(self) -> str:
        return self.data["start_time"]

    @property
    def stop_time(self) -> str:
        return self.data["stop_time"]

    @property
    def map_view(self) -> str:
        return self.data["map_view"]

    @property
    def volume(self) -> str:
        return self.data["volume"]

    @property
    def voice_package(self) -> str:
        return self.data["voice_package"]

    @property
    def timezone(self) -> str:
        return self.data["timezone"]

    @property
    def cleaning_time(self) -> str:
        return self.data["cleaning_time"]

    @property
    def cleaning_area(self) -> str:
        return self.data["cleaning_area"]

    @property
    def first_clean_time(self) -> str:
        return self.data["first_clean_time"]

    @property
    def total_clean_time(self) -> str:
        return self.data["total_clean_time"]

    @property
    def total_clean_times(self) -> str:
        return self.data["total_clean_times"]

    @property
    def total_clean_area(self) -> str:
        return self.data["total_clean_area"]


class Dreame1CVacuumStatus(DreameVacuumStatusBase):
    @property
    def cleaning_mode(self) -> CleaningModeDreame1C:
        try:
            return CleaningModeDreame1C(self.data["cleaning_mode"])
        except ValueError:
            _LOGGER.error("Unknown CleaningMode (%s)", self.data["cleaning_mode"])
            return CleaningModeDreame1C.Unknown

    @property
    def life_sieve(self) -> str:
        return self.data["life_sieve"]

    @property
    def life_brush_side(self) -> str:
        return self.data["life_brush_side"]

    @property
    def life_brush_main(self) -> str:
        return self.data["life_brush_main"]


class DreameF9VacuumStatus(DreameVacuumStatusBase):
    @property
    def water_flow(self) -> WaterFlow:
        try:
            return WaterFlow(self.data["water_flow"])
        except ValueError:
            _LOGGER.error("Unknown WaterFlow (%s)", self.data["water_flow"])
            return WaterFlow.Unknown

    @property
    def water_tank_status(self) -> WaterTankStatus:
        try:
            return WaterTankStatus(self.data["water_tank_status"])
        except ValueError:
            _LOGGER.error("Unknown WaterFlow (%s)", self.data["water_tank_status"])
            return WaterTankStatus.Unknown

    @property
    def cleaning_mode(self) -> CleaningModeDreameF9:
        try:
            return CleaningModeDreameF9(self.data["cleaning_mode"])
        except ValueError:
            _LOGGER.error("Unknown CleaningMode (%s)", self.data["cleaning_mode"])
            return CleaningModeDreameF9.Unknown


class DreameVacuumBase(MiotDevice):
    # TODO: check the actual limit for this
    MANUAL_ROTATION_MAX = 120
    MANUAL_ROTATION_MIN = -MANUAL_ROTATION_MAX
    MANUAL_DISTANCE_MAX = 300
    MANUAL_DISTANCE_MIN = -300

    @command()
    def start(self) -> None:
        """Start cleaning."""
        return self.call_action("start_clean")

    @command()
    def stop(self) -> None:
        """Stop cleaning."""
        return self.call_action("stop_clean")

    @command()
    def home(self) -> None:
        """Return to home."""
        return self.call_action("home")

    @command()
    def identify(self) -> None:
        """Locate the device (i am here)."""
        return self.call_action("locate")

    @command()
    def reset_mainbrush_life(self) -> None:
        """Reset main brush life."""
        return self.call_action("reset_mainbrush_life")

    @command()
    def reset_filter_life(self) -> None:
        """Reset filter life."""
        return self.call_action("reset_filter_life")

    @command()
    def reset_sidebrush_life(self) -> None:
        """Reset side brush life."""
        return self.call_action("reset_sidebrush_life")

    @command()
    def play_sound(self) -> None:
        """Play sound."""
        return self.call_action("play_sound")

    @command(
        click.argument("distance", default=30, type=int),
    )
    def forward(self, distance: int) -> None:
        """Move forward."""
        if distance < self.MANUAL_DISTANCE_MIN or distance > self.MANUAL_DISTANCE_MAX:
            raise DeviceException(
                "Given distance is invalid, should be [%s, %s], was: %s"
                % (self.MANUAL_DISTANCE_MIN, self.MANUAL_DISTANCE_MAX, distance)
            )
        self.call_action(
            "move",
            [
                {
                    "piid": 1,
                    "value": "0",
                },
                {
                    "piid": 2,
                    "value": f"{distance}",
                },
            ],
        )

    @command(
        click.argument("rotatation", default=90, type=int),
    )
    def rotate(self, rotatation: int) -> None:
        """Rotate vacuum."""
        if (
            rotatation < self.MANUAL_ROTATION_MIN
            or rotatation > self.MANUAL_ROTATION_MAX
        ):
            raise DeviceException(
                "Given rotation is invalid, should be [%s, %s], was %s"
                % (self.MANUAL_ROTATION_MIN, self.MANUAL_ROTATION_MAX, rotatation)
            )
        self.call_action(
            "move",
            [
                {
                    "piid": 1,
                    "value": f"{rotatation}",
                },
                {
                    "piid": 2,
                    "value": "0",
                },
            ],
        )


class Dreame1CVacuum(DreameVacuumBase):
    """Interface for Vacuum 1C STYTJ01ZHM (dreame.vacuum.mc1808)"""

    _supported_models = [
        DREAME_1C,
    ]
    mapping = MIOT_MAPPING[DREAME_1C]

    @command(
        default_output=format_output(
            "\n",
            "Battery level: {result.battery_level}\n"
            "Brush life level: {result.brush_life_level}\n"
            "Brush left time: {result.brush_left_time}\n"
            "Charging state: {result.charging_state.name}\n"
            "Cleaning mode: {result.cleaning_mode.name}\n"
            "Device fault: {result.device_fault.name}\n"
            "Device status: {result.device_status.name}\n"
            "Filter left level: {result.filter_left_time}\n"
            "Filter life level: {result.filter_life_level}\n"
            "Life brush main: {result.life_brush_main}\n"
            "Life brush side: {result.life_brush_side}\n"
            "Life sieve: {result.life_sieve}\n"
            "Map view: {result.map_view}\n"
            "Operating mode: {result.operating_mode.name}\n"
            "Side cleaning brush left time: {result.brush_left_time2}\n"
            "Side cleaning brush life level: {result.brush_life_level2}\n"
            "Time zone: {result.timezone}\n"
            "Timer enabled: {result.timer_enable}\n"
            "Timer start time: {result.start_time}\n"
            "Timer stop time: {result.stop_time}\n"
            "Voice package: {result.voice_package}\n"
            "Volume: {result.volume}\n"
            "Cleaning time: {result.cleaning_time}\n"
            "Cleaning area: {result.cleaning_area}\n"
            "First clean time: {result.first_clean_time}\n"
            "Total clean time: {result.total_clean_time}\n"
            "Total clean times: {result.total_clean_times}\n"
            "Total clean area: {result.total_clean_area}\n",
        )
    )
    def status(self) -> Dreame1CVacuumStatus:
        """State of the vacuum."""

        return Dreame1CVacuumStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping(max_properties=10)
            }
        )


class DreameVacuumMiot(Dreame1CVacuum):
    @deprecated(
        "This class is replaced with Dreame1CVacuum. Use Dreame1CVacuum to control Dreame 1C vacuums."
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DreameF9Vacuum(DreameVacuumBase):
    """Interface for Vacuum F9 (dreame.vacuum.p2008)"""

    _supported_models = [
        DREAME_F9,
    ]
    mapping = MIOT_MAPPING[DREAME_F9]

    @command(
        default_output=format_output(
            "\n",
            "Battery level: {result.battery_level}\n"
            "Brush life level: {result.brush_life_level}\n"
            "Brush left time: {result.brush_left_time}\n"
            "Charging state: {result.charging_state.name}\n"
            "Cleaning mode: {result.cleaning_mode.name}\n"
            "Device fault: {result.device_fault.name}\n"
            "Device status: {result.device_status.name}\n"
            "Filter left level: {result.filter_left_time}\n"
            "Filter life level: {result.filter_life_level}\n"
            "Map view: {result.map_view}\n"
            "Operating mode: {result.operating_mode.name}\n"
            "Side cleaning brush left time: {result.brush_left_time2}\n"
            "Side cleaning brush life level: {result.brush_life_level2}\n"
            "Time zone: {result.timezone}\n"
            "Timer enabled: {result.timer_enable}\n"
            "Timer start time: {result.start_time}\n"
            "Timer stop time: {result.stop_time}\n"
            "Voice package: {result.voice_package}\n"
            "Volume: {result.volume}\n"
            "Water flow: {result.water_flow.name}\n"
            "Water tank status: {result.water_tank_status.name}\n"
            "Cleaning time: {result.cleaning_time}\n"
            "Cleaning area: {result.cleaning_area}\n"
            "First clean time: {result.first_clean_time}\n"
            "Total clean time: {result.total_clean_time}\n"
            "Total clean times: {result.total_clean_times}\n"
            "Total clean area: {result.total_clean_area}\n",
        )
    )
    def status(self) -> DreameF9VacuumStatus:
        """State of the vacuum."""

        return DreameF9VacuumStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping(max_properties=10)
            }
        )
