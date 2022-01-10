"""Vacuum Dreame Vacuum F9 (dreame.vacuum.p2008)"""

import logging
from enum import Enum

import click

from miio.click_common import command, format_output
from miio.exceptions import DeviceException
from miio.miot_device import DeviceStatus as DeviceStatusContainer
from miio.miot_device import MiotDevice, MiotMapping

_LOGGER = logging.getLogger(__name__)

_MAPPING: MiotMapping = {
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
    "start_time": {"siid": 5, "piid": 2},
    "stop_time": {"siid": 5, "piid": 3},
    "map_view": {"siid": 6, "piid": 1},
    "frame_info": {"siid": 6, "piid": 2},
    "volume": {"siid": 7, "piid": 1},
    "voice_package": {"siid": 7, "piid": 2},
    "water_flow": {"siid": 4, "piid": 5},
    "water_tank_status": {"siid": 4, "piid": 6},
    "time_zone": {"siid": 8, "piid": 1},
    "home": {"siid": 3, "aiid": 1},
    "locate": {"siid": 7, "aiid": 1},
    "start_clean": {"siid": 4, "aiid": 1},
    "stop_clean": {"siid": 4, "aiid": 2},
    "reset_mainbrush_life": {"siid": 9, "aiid": 1},
    "reset_filter_life": {"siid": 11, "aiid": 1},
    "reset_sidebrush_life": {"siid": 10, "aiid": 1},
    "move": {"siid": 21, "aiid": 1},
}


class ChargingState(Enum):
    Unknown = -1
    Charging = 1
    Discharging = 2
    GoCharging = 5


class CleaningMode(Enum):
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


class WaterFlow(Enum):
    Unknown = -1
    Low = 1
    Medium = 2
    High = 3


class WaterTankStatus(Enum):
    Unknown = -1
    NotAttached = 0
    Attached = 1


class DreameF9VacuumStatus(DeviceStatusContainer):
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
    def cleaning_mode(self) -> CleaningMode:
        try:
            return CleaningMode(self.data["cleaning_mode"])
        except ValueError:
            _LOGGER.error("Unknown CleaningMode (%s)", self.data["cleaning_mode"])
            return CleaningMode.Unknown

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
    def time_zone(self) -> str:
        return self.data["time_zone"]


class DreameF9VacuumMiot(MiotDevice):
    """Interface for Vacuum F9 (dreame.vacuum.p2008)"""

    mapping = _MAPPING

    _supported_models = [
        "dreame.vacuum.p2008",
    ]

    # TODO: check the actual limit for this
    MANUAL_ROTATION_MAX = 120
    MANUAL_ROTATION_MIN = -MANUAL_ROTATION_MAX
    MANUAL_DISTANCE_MAX = 300
    MANUAL_DISTANCE_MIN = -300

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
            "Time zone: {result.time_zone}\n"
            "Timer enabled: {result.timer_enable}\n"
            "Timer start time: {result.start_time}\n"
            "Timer stop time: {result.stop_time}\n"
            "Voice package: {result.voice_package}\n"
            "Volume: {result.volume}\n"
            "Water flow: {result.water_flow.name}\n"
            "Water tank status: {result.water_tank_status.name}\n",
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
        """Move forward."""
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
