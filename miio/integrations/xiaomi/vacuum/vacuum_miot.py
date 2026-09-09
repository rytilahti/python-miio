import json
import logging
from datetime import timedelta
from enum import Enum

import click

from miio.click_common import EnumType, command, format_output
from miio.miot_device import DeviceStatus, MiotDevice, MiotMapping

_LOGGER = logging.getLogger(__name__)

XIAOMI_VACUUM_E101GB = "xiaomi.vacuum.e101gb"

_MAPPING: MiotMapping = {
    "status": {"siid": 2, "piid": 2},
    "fault": {"siid": 2, "piid": 3},
    "cleaning_area": {"siid": 2, "piid": 6},
    "cleaning_time": {"siid": 2, "piid": 7},
    "mode": {"siid": 2, "piid": 9},
    "water_level": {"siid": 2, "piid": 10},
    "mop_status": {"siid": 2, "piid": 11},
    "zone_ids": {"siid": 2, "piid": 12},
    "room_information": {"siid": 2, "piid": 16},
    "battery_level": {"siid": 3, "piid": 1},
    "main_brush_life_level": {"siid": 12, "piid": 1},
    "main_brush_left_time": {"siid": 12, "piid": 2},
    "side_brush_life_level": {"siid": 13, "piid": 1},
    "side_brush_left_time": {"siid": 13, "piid": 2},
    "filter_life_level": {"siid": 14, "piid": 1},
    "filter_left_time": {"siid": 14, "piid": 2},
    "start": {"siid": 2, "aiid": 1},
    "stop": {"siid": 2, "aiid": 2},
    "home": {"siid": 2, "aiid": 3},
    "pause": {"siid": 2, "aiid": 7},
    "resume": {"siid": 2, "aiid": 8},
    "get_zone_configs": {"siid": 2, "aiid": 10},
    "get_room_configs": {"siid": 2, "aiid": 11},
    "set_zone": {"siid": 2, "aiid": 12},
    "set_room_clean_configs": {"siid": 2, "aiid": 13},
    "start_vacuum_room_sweep": {"siid": 2, "aiid": 16},
    "start_zone_sweep": {"siid": 2, "aiid": 37},
    "find": {"siid": 6, "aiid": 1},
    "reset_main_brush_life": {"siid": 12, "aiid": 1},
    "reset_side_brush_life": {"siid": 13, "aiid": 1},
    "reset_filter_life": {"siid": 14, "aiid": 1},
}

_MAPPINGS: dict[str, MiotMapping] = {XIAOMI_VACUUM_E101GB: _MAPPING}

_STATUS_KEYS = [
    "status",
    "fault",
    "battery_level",
    "mode",
    "water_level",
    "mop_status",
    "cleaning_area",
    "cleaning_time",
    "main_brush_life_level",
    "main_brush_left_time",
    "side_brush_life_level",
    "side_brush_left_time",
    "filter_life_level",
    "filter_left_time",
]


class VacuumStatus(Enum):
    Idle = 1
    Charging = 2
    BreakCharging = 3
    Sweeping = 4
    Paused = 5
    GoCharging = 6
    GoWash = 7
    Remote = 8
    Charged = 9
    BuildingMap = 10
    Updating = 11
    MultiTaskStationWorking = 12
    MultiTaskRecharge = 13
    StationWorking = 14
    Error = 15
    SweepingAndMopping = 16
    Mopping = 17
    MappingPause = 18
    GoChargeBreak = 19
    WashBreak = 20
    GoChargeBuildingMap = 21
    StationAssistingCleaning = 22
    StationAssistingCleaned = 23
    GoChargeInStationAssistingCleaning = 24


class FanSpeed(Enum):
    Silent = 1
    Basic = 2
    Strong = 3
    FullSpeed = 4


class WaterLevel(Enum):
    Off = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3


class Consumable(Enum):
    MainBrush = "main_brush"
    SideBrush = "side_brush"
    Filter = "filter"


class XiaomiVacuumE101GBStatus(DeviceStatus):
    """Container for Xiaomi Robot Vacuum S40C / E101GB status."""

    def __init__(self, data):
        self.data = data

    @property
    def battery(self) -> int:
        return self.data["battery_level"]

    @property
    def status(self) -> VacuumStatus:
        return VacuumStatus(self.data["status"])

    @property
    def error_code(self) -> int:
        return int(self.data["fault"])

    @property
    def fan_speed(self) -> FanSpeed:
        return FanSpeed(self.data["mode"])

    @property
    def water_level(self) -> WaterLevel:
        return WaterLevel(self.data["water_level"])

    @property
    def mop_status(self) -> bool:
        return bool(self.data["mop_status"])

    @property
    def cleaning_area(self) -> int:
        return self.data["cleaning_area"]

    @property
    def cleaning_time(self) -> timedelta:
        return timedelta(seconds=self.data["cleaning_time"])

    @property
    def main_brush_life_level(self) -> int:
        return self.data["main_brush_life_level"]

    @property
    def main_brush_left_time(self) -> timedelta:
        return timedelta(hours=self.data["main_brush_left_time"])

    @property
    def side_brush_life_level(self) -> int:
        return self.data["side_brush_life_level"]

    @property
    def side_brush_left_time(self) -> timedelta:
        return timedelta(hours=self.data["side_brush_left_time"])

    @property
    def filter_life_level(self) -> int:
        return self.data["filter_life_level"]

    @property
    def filter_left_time(self) -> timedelta:
        return timedelta(hours=self.data["filter_left_time"])


class XiaomiVacuumE101GB(MiotDevice):
    """Support for Xiaomi Robot Vacuum S40C EU."""

    _mappings = _MAPPINGS

    def _get_properties_for_keys(self, keys: list[str]) -> dict[str, object]:
        mapping = self._get_mapping()
        props = [{"did": key, **mapping[key]} for key in keys]
        key_by_prop_id = {
            (mapping[key]["siid"], mapping[key]["piid"]): key for key in keys
        }
        response = self.get_properties(
            props, property_getter="get_properties", max_properties=6
        )
        values = {}
        for prop in response:
            siid = prop.get("siid")
            piid = prop.get("piid")
            key = None
            if siid is not None and piid is not None:
                key = key_by_prop_id.get((siid, piid))
            if key is None:
                key = prop.get("did")
            if key is None:
                _LOGGER.debug("Ignoring unexpected property response: %s", prop)
                continue

            values[key] = prop["value"] if prop["code"] == 0 else None

        return values

    def _action_input(self, piid: int, value: object) -> list[dict[str, object]]:
        """Create an action payload for a MIoT action input property."""
        return [{"piid": piid, "value": value}]

    def _get_single_property(self, key: str):
        """Read a single mapped MIoT property."""
        return self._get_properties_for_keys([key]).get(key)

    @command(
        default_output=format_output(
            "",
            "Status: {result.status}\n"
            "Error: {result.error_code}\n"
            "Battery: {result.battery}%\n"
            "Fan speed: {result.fan_speed}\n"
            "Water level: {result.water_level}\n"
            "Mop mounted: {result.mop_status}\n"
            "Cleaning area: {result.cleaning_area}\n"
            "Cleaning time: {result.cleaning_time}\n"
            "Main brush life: "
            "{result.main_brush_life_level}% ({result.main_brush_left_time})\n"
            "Side brush life: "
            "{result.side_brush_life_level}% ({result.side_brush_left_time})\n"
            "Filter life: {result.filter_life_level}% ({result.filter_left_time})\n",
        )
    )
    def status(self) -> XiaomiVacuumE101GBStatus:
        """Return a stable subset of vacuum status.

        The generic MIoT status query for this model is too wide and can time out,
        so we intentionally query the core properties in small batches.
        """
        data = {}
        for idx in range(0, len(_STATUS_KEYS), 6):
            data.update(self._get_properties_for_keys(_STATUS_KEYS[idx : idx + 6]))

        return XiaomiVacuumE101GBStatus(data)

    @command()
    def start(self):
        return self.call_action_from_mapping("start")

    @command()
    def stop(self):
        return self.call_action_from_mapping("stop")

    @command()
    def pause(self):
        return self.call_action_from_mapping("pause")

    @command()
    def resume(self):
        return self.call_action_from_mapping("resume")

    @command()
    def home(self):
        return self.call_action_from_mapping("home")

    @command()
    def find(self):
        return self.call_action_from_mapping("find")

    @command(click.argument("room_ids", type=str))
    def start_room_sweep(self, room_ids: str):
        """Start cleaning one or more room ids."""
        return self.call_action_from_mapping(
            "start_vacuum_room_sweep", params=self._action_input(15, room_ids)
        )

    @command(click.argument("zone_ids", type=str))
    def start_zone_sweep(self, zone_ids: str):
        """Start cleaning one or more zone definitions."""
        return self.call_action_from_mapping(
            "start_zone_sweep", params=self._action_input(12, zone_ids)
        )

    @command(click.argument("room_ids", type=str))
    def get_room_configs(self, room_ids: str):
        """Return room config payload for provided room ids."""
        return self.call_action_from_mapping(
            "get_room_configs", params=self._action_input(15, room_ids)
        )

    @command(click.argument("zone_ids", type=str))
    def get_zone_configs(self, zone_ids: str):
        """Return zone config payload for provided zone ids."""
        return self.call_action_from_mapping(
            "get_zone_configs", params=self._action_input(12, zone_ids)
        )

    @command()
    def room_information(self) -> dict:
        """Return parsed room metadata for the current map."""
        value = self._get_single_property("room_information")
        if not value:
            return {}
        return json.loads(value)

    @command()
    def room_ids(self) -> list[int]:
        """Return available room ids for room-based cleaning."""
        info = self.room_information()
        return [room["id"] for room in info.get("rooms", []) if "id" in room]

    @command()
    def zone_ids(self) -> str:
        """Return raw zone ids payload advertised by the device."""
        value = self._get_single_property("zone_ids")
        return "" if value is None else value

    @command()
    def reset_main_brush_life(self):
        return self.call_action_from_mapping("reset_main_brush_life")

    @command()
    def reset_side_brush_life(self):
        return self.call_action_from_mapping("reset_side_brush_life")

    @command()
    def reset_filter_life(self):
        return self.call_action_from_mapping("reset_filter_life")

    @command(click.argument("consumable", type=Consumable))
    def consumable_reset(self, consumable: Consumable):
        if consumable == Consumable.MainBrush:
            return self.reset_main_brush_life()
        if consumable == Consumable.SideBrush:
            return self.reset_side_brush_life()
        return self.reset_filter_life()

    @command()
    def fan_speed_presets(self) -> dict[str, int]:
        return {speed.name: speed.value for speed in FanSpeed}

    @command(click.argument("speed", type=EnumType(FanSpeed)))
    def set_fan_speed(self, speed: FanSpeed):
        return self.set_property("mode", speed.value)

    @command(click.argument("speed", type=int))
    def set_fan_speed_preset(self, speed: int):
        if speed not in self.fan_speed_presets().values():
            raise ValueError(
                "Invalid preset speed "
                f"{speed}, not in: {self.fan_speed_presets().values()}"
            )
        return self.set_property("mode", speed)

    @command()
    def water_level_presets(self) -> dict[str, int]:
        return {level.name: level.value for level in WaterLevel}

    @command(click.argument("level", type=EnumType(WaterLevel)))
    def set_water_level(self, level: WaterLevel):
        return self.set_property("water_level", level.value)
