"""Vacuum 1C STYTJ01ZHM (dreame.vacuum.mc1808)"""

import logging
from enum import Enum

from .click_common import command, format_output
from .miot_device import DeviceStatus as DeviceStatusContainer
from .miot_device import MiotDevice, MiotMapping

_LOGGER = logging.getLogger(__name__)

_MAPPING: MiotMapping = {
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
}


class ChargingState(Enum):
    Unknown = -1
    Charging = 1
    Discharging = 2
    Charging2 = 4
    GoCharging = 5


class CleaningMode(Enum):
    Unknown = -1
    Quiet = 0
    Default = 1
    Medium = 2
    Strong = 3


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


class DreameVacuumStatus(DeviceStatusContainer):
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
    def life_sieve(self) -> str:
        return self.data["life_sieve"]

    @property
    def life_brush_side(self) -> str:
        return self.data["life_brush_side"]

    @property
    def life_brush_main(self) -> str:
        return self.data["life_brush_main"]

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


class DreameVacuumMiot(MiotDevice):
    """Interface for Vacuum 1C STYTJ01ZHM (dreame.vacuum.mc1808)"""

    mapping = _MAPPING

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
            "Timer enabled: {result.timer_enable}\n"
            "Timer start time: {result.start_time}\n"
            "Timer stop time: {result.stop_time}\n"
            "Voice package: {result.voice_package}\n"
            "Volume: {result.volume}\n",
        )
    )
    def status(self) -> DreameVacuumStatus:
        """State of the vacuum."""

        return DreameVacuumStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping(max_properties=10)
            }
        )

    def send_action(self, siid, aiid, params=None):
        """Send action to device."""

        # {"did":"<mydeviceID>","siid":18,"aiid":1,"in":[{"piid":1,"value":2}]
        if params is None:
            params = []
        payload = {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        }
        return self.send("action", payload)

    @command()
    def start(self) -> None:
        """Start cleaning."""
        return self.send_action(3, 1)

    @command()
    def stop(self) -> None:
        """Stop cleaning."""
        return self.send_action(3, 2)

    @command()
    def home(self) -> None:
        """Return to home."""
        return self.send_action(2, 1)

    @command()
    def identify(self) -> None:
        """Locate the device (i am here)."""
        return self.send_action(17, 1)

    @command()
    def reset_mainbrush_life(self) -> None:
        """Reset main brush life."""
        return self.send_action(26, 1)

    @command()
    def reset_filter_life(self) -> None:
        """Reset filter life."""
        return self.send_action(27, 1)

    @command()
    def reset_sidebrush_life(self) -> None:
        """Reset side brush life."""
        return self.send_action(28, 1)
