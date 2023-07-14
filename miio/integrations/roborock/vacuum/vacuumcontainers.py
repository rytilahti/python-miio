import logging
from datetime import datetime, time, timedelta
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

from croniter import croniter
from pytz import BaseTzInfo

from miio.device import DeviceStatus
from miio.devicestatus import sensor, setting
from miio.identifiers import VacuumId, VacuumState
from miio.utils import pretty_seconds, pretty_time

from .vacuum_enums import MopIntensity, MopMode

_LOGGER = logging.getLogger(__name__)


def pretty_area(x: float) -> float:
    return int(x) / 1000000


STATE_CODE_TO_STRING = {
    1: "Starting",
    2: "Charger disconnected",
    3: "Idle",
    4: "Remote control active",
    5: "Cleaning",
    6: "Returning home",
    7: "Manual mode",
    8: "Charging",
    9: "Charging problem",
    10: "Paused",
    11: "Spot cleaning",
    12: "Error",
    13: "Shutting down",
    14: "Updating",
    15: "Docking",
    16: "Going to target",
    17: "Zoned cleaning",
    18: "Segment cleaning",
    22: "Emptying the bin",  # on s7+, see #1189
    23: "Washing the mop",  # on a46, #1435
    26: "Going to wash the mop",  # on a46, #1435
    100: "Charging complete",
    101: "Device offline",
}

VACUUMSTATE_TO_STATE_CODES = {
    VacuumState.Idle: [1, 2, 3, 13],
    VacuumState.Paused: [10],
    VacuumState.Cleaning: [4, 5, 7, 11, 16, 17, 18],
    VacuumState.Docked: [8, 14, 22, 100],
    VacuumState.Returning: [6, 15],
    VacuumState.Error: [9, 12, 101],
}
STATE_CODE_TO_VACUUMSTATE = {}
for state, codes in VACUUMSTATE_TO_STATE_CODES.items():
    for code in codes:
        STATE_CODE_TO_VACUUMSTATE[code] = state


ERROR_CODES = {  # from vacuum_cleaner-EN.pdf
    0: "No error",
    1: "Laser distance sensor error",
    2: "Collision sensor error",
    3: "Wheels on top of void, move robot",
    4: "Clean hovering sensors, move robot",
    5: "Clean main brush",
    6: "Clean side brush",
    7: "Main wheel stuck?",
    8: "Device stuck, clean area",
    9: "Dust collector missing",
    10: "Clean filter",
    11: "Stuck in magnetic barrier",
    12: "Low battery",
    13: "Charging fault",
    14: "Battery fault",
    15: "Wall sensors dirty, wipe them",
    16: "Place me on flat surface",
    17: "Side brushes problem, reboot me",
    18: "Suction fan problem",
    19: "Unpowered charging station",
    21: "Laser distance sensor blocked",
    22: "Clean the dock charging contacts",
    23: "Docking station not reachable",
    24: "No-go zone or invisible wall detected",
    26: "Wall sensor is dirty",
    27: "VibraRise system is jammed",
    28: "Roborock is on carpet",
}

dock_error_codes = {  # from vacuum_cleaner-EN.pdf
    0: "No error",
    38: "Clean water tank empty",
    39: "Dirty water tank full",
}


class MapList(DeviceStatus):
    """Contains a information about the maps/floors of the vacuum."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'max_multi_map': 4, 'max_bak_map': 1, 'multi_map_count': 3, 'map_info': [
        #    {'mapFlag': 0, 'add_time': 1664448893, 'length': 10, 'name': 'Downstairs', 'bak_maps': [{'mapFlag': 4, 'add_time': 1663577737}]},
        #    {'mapFlag': 1, 'add_time': 1663580330, 'length': 8, 'name': 'Upstairs', 'bak_maps': [{'mapFlag': 5, 'add_time': 1663577752}]},
        #    {'mapFlag': 2, 'add_time': 1663580384, 'length': 5, 'name': 'Attic', 'bak_maps': [{'mapFlag': 6, 'add_time': 1663577765}]}
        #  ]}
        self.data = data

        self._map_name_dict = {}
        for map in self.data["map_info"]:
            self._map_name_dict[map["name"]] = map["mapFlag"]

    @property
    def map_count(self) -> int:
        """Amount of maps stored."""
        return self.data["multi_map_count"]

    @property
    def map_id_list(self) -> List[int]:
        """List of map ids."""
        return list(self._map_name_dict.values())

    @property
    def map_list(self) -> List[Dict[str, Any]]:
        """List of map info."""
        return self.data["map_info"]

    @property
    def map_name_dict(self) -> Dict[str, int]:
        """Dictionary of map names (keys) with there ids (values)."""
        return self._map_name_dict


class VacuumStatus(DeviceStatus):
    """Container for status reports from the vacuum."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'result': [{'state': 8, 'dnd_enabled': 1, 'clean_time': 0,
        #  'msg_ver': 4, 'map_present': 1, 'error_code': 0, 'in_cleaning': 0,
        #  'clean_area': 0, 'battery': 100, 'fan_power': 20, 'msg_seq': 320}],
        #  'id': 1}

        # v8 new items
        # clean_mode, begin_time, clean_trigger,
        # back_trigger, clean_strategy, and completed
        # TODO: create getters if wanted
        #
        # {"msg_ver":8,"msg_seq":60,"state":5,"battery":93,"clean_mode":0,
        # "fan_power":50,"error_code":0,"map_present":1,"in_cleaning":1,
        # "dnd_enabled":0,"begin_time":1534333389,"clean_time":21,
        # "clean_area":202500,"clean_trigger":2,"back_trigger":0,
        # "completed":0,"clean_strategy":1}

        # Example of S6 in the segment cleaning mode
        # new items: in_fresh_state, water_box_status, lab_status, map_status, lock_status
        #
        # [{'msg_ver': 2, 'msg_seq': 28, 'state': 18, 'battery': 95,
        # 'clean_time': 606, 'clean_area': 8115000, 'error_code': 0,
        # 'map_present': 1, 'in_cleaning': 3, 'in_returning': 0,
        # 'in_fresh_state': 0, 'lab_status': 1, 'water_box_status': 0,
        # 'fan_power': 102, 'dnd_enabled': 0, 'map_status': 3, 'lock_status': 0}]

        # Example of S7 in charging mode
        # new items: is_locating, water_box_mode, water_box_carriage_status,
        # mop_forbidden_enable, adbumper_status, water_shortage_status,
        # dock_type, dust_collection_status, auto_dust_collection, mop_mode, debug_mode
        #
        # [{'msg_ver': 2, 'msg_seq': 1839, 'state': 8, 'battery': 100,
        # 'clean_time': 2311, 'clean_area': 35545000, 'error_code': 0,
        # 'map_present': 1, 'in_cleaning': 0, 'in_returning': 0,
        # 'in_fresh_state': 1, 'lab_status': 3, 'water_box_status': 1,
        # 'fan_power': 102, 'dnd_enabled': 0, 'map_status': 3, 'is_locating': 0,
        # 'lock_status': 0, 'water_box_mode': 202, 'water_box_carriage_status': 0,
        # 'mop_forbidden_enable': 0, 'adbumper_status': [0, 0, 0],
        # 'water_shortage_status': 0, 'dock_type': 0, 'dust_collection_status': 0,
        # 'auto_dust_collection': 1,  'mop_mode': 300, 'debug_mode': 0}]
        self.data = data

    @property
    @sensor("State code", entity_category="diagnostic", enabled_default=False)
    def state_code(self) -> int:
        """State code as returned by the device."""
        return int(self.data["state"])

    @property
    @sensor("State", entity_category="diagnostic")
    def state(self) -> str:
        """Human readable state description, see also :func:`state_code`."""
        return STATE_CODE_TO_STRING.get(
            self.state_code, f"Unknown state (code: {self.state_code})"
        )

    @sensor("Vacuum state", id=VacuumId.State)
    def vacuum_state(self) -> VacuumState:
        """Return vacuum state."""
        return STATE_CODE_TO_VACUUMSTATE.get(self.state_code, VacuumState.Unknown)

    @property
    @sensor(
        "Error code",
        icon="mdi:alert",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    @sensor(
        "Error string",
        id=VacuumId.ErrorMessage,
        icon="mdi:alert",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def error(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        try:
            return ERROR_CODES[self.error_code]
        except KeyError:
            return "Definition missing for error %s" % self.error_code

    @property
    @sensor(
        "Dock error code",
        icon="mdi:alert",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def dock_error_code(self) -> Optional[int]:
        """Dock error status as returned by the device."""
        if "dock_error_status" in self.data:
            return int(self.data["dock_error_status"])
        return None

    @property
    @sensor(
        "Dock error string",
        icon="mdi:alert",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def dock_error(self) -> Optional[str]:
        """Human readable dock error description, see also :func:`dock_error_code`."""
        if self.dock_error_code is None:
            return None
        try:
            return dock_error_codes[self.dock_error_code]
        except KeyError:
            return "Definition missing for dock error %s" % self.dock_error_code

    @property
    @sensor("Battery", unit="%", id=VacuumId.Battery)
    def battery(self) -> int:
        """Remaining battery in percentage."""
        return int(self.data["battery"])

    @property
    @setting(
        "Fanspeed",
        unit="%",
        setter_name="set_fan_speed",
        min_value=0,
        max_value=100,
        step=1,
        icon="mdi:fan",
    )
    def fanspeed(self) -> Optional[int]:
        """Current fan speed."""
        fan_power = int(self.data["fan_power"])
        if fan_power > 100:
            # values 100+ are reserved for presets
            return None
        return fan_power

    @property
    @setting(
        "Mop scrub intensity",
        choices=MopIntensity,
        setter_name="set_mop_intensity",
        icon="mdi:checkbox-multiple-blank-circle-outline",
    )
    def mop_intensity(self) -> Optional[int]:
        """Current mop intensity."""
        if "water_box_mode" in self.data:
            return int(self.data["water_box_mode"])
        return None

    @property
    @setting(
        "Mop route",
        choices=MopMode,
        setter_name="set_mop_mode",
        icon="mdi:swap-horizontal-variant",
    )
    def mop_route(self) -> Optional[int]:
        """Current mop route."""
        if "mop_mode" in self.data:
            return int(self.data["mop_mode"])
        return None

    @property
    @sensor(
        "Current clean duration",
        unit="s",
        icon="mdi:timer-sand",
        device_class="duration",
    )
    def clean_time(self) -> timedelta:
        """Time used for cleaning (if finished, shows how long it took)."""
        return pretty_seconds(self.data["clean_time"])

    @property
    @sensor("Current clean area", unit="m²", icon="mdi:texture-box")
    def clean_area(self) -> float:
        """Cleaned area in m2."""
        return pretty_area(self.data["clean_area"])

    @property
    def map(self) -> bool:
        """Map token."""
        return bool(self.data["map_present"])

    @property
    @setting(
        "Current map",
        choices_attribute="_map_enum",
        setter_name="load_map",
        icon="mdi:floor-plan",
    )
    def current_map_id(self) -> Optional[int]:
        """The id of the current map with regards to the multi map feature,

        [3,7,11,15] -> [0,1,2,3].
        """
        try:
            return int((self.data["map_status"] + 1) / 4 - 1)
        except KeyError:
            return None

    @property
    def in_zone_cleaning(self) -> bool:
        """Return True if the vacuum is in zone cleaning mode."""
        return self.data["in_cleaning"] == 2

    @property
    def in_segment_cleaning(self) -> bool:
        """Return True if the vacuum is in segment cleaning mode."""
        return self.data["in_cleaning"] == 3

    @property
    def is_paused(self) -> bool:
        """Return True if vacuum is paused."""
        return self.state_code == 10

    @property
    def is_on(self) -> bool:
        """True if device is currently cleaning in any mode."""
        return (
            self.state_code == 5
            or self.state_code == 7
            or self.state_code == 11
            or self.state_code == 17
            or self.state_code == 18
        )

    @property
    @sensor("Water box attached", icon="mdi:cup-water")
    def is_water_box_attached(self) -> Optional[bool]:
        """Return True is water box is installed."""
        if "water_box_status" in self.data:
            return self.data["water_box_status"] == 1
        return None

    @property
    @sensor("Mop attached")
    def is_water_box_carriage_attached(self) -> Optional[bool]:
        """Return True if water box carriage (mop) is installed, None if sensor not
        present."""
        if "water_box_carriage_status" in self.data:
            return self.data["water_box_carriage_status"] == 1
        return None

    @property
    @sensor("Water level low", icon="mdi:water-alert-outline")
    def is_water_shortage(self) -> Optional[bool]:
        """Returns True if water is low in the tank, None if sensor not present."""
        if "water_shortage_status" in self.data:
            return self.data["water_shortage_status"] == 1
        return None

    @property
    @setting(
        "Auto dust collection",
        setter_name="set_dust_collection",
        icon="mdi:turbine",
        entity_category="config",
    )
    def auto_dust_collection(self) -> Optional[bool]:
        """Returns True if auto dust collection is enabled, None if sensor not
        present."""
        if "auto_dust_collection" in self.data:
            return self.data["auto_dust_collection"] == 1
        return None

    @property
    @sensor(
        "Error", icon="mdi:alert", entity_category="diagnostic", enabled_default=False
    )
    def got_error(self) -> bool:
        """True if an error has occurred."""
        return self.error_code != 0

    @property
    @sensor(
        "Mop is drying",
        icon="mdi:tumble-dryer",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def is_mop_drying(self) -> Optional[bool]:
        """Return if mop drying is running."""
        if "dry_status" in self.data:
            return self.data["dry_status"] == 1
        return None

    @property
    @sensor(
        "Dryer remaining seconds",
        unit="s",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def mop_dryer_remaining_seconds(self) -> Optional[timedelta]:
        """Return remaining mop drying seconds."""
        if "rdt" in self.data:
            return pretty_seconds(self.data["rdt"])
        return None


class CleaningSummary(DeviceStatus):
    """Contains summarized information about available cleaning runs."""

    def __init__(self, data: Union[List[Any], Dict[str, Any]]) -> None:
        # total duration, total area, amount of cleans
        # [ list, of, ids ]
        # { "result": [ 174145, 2410150000, 82,
        # [ 1488240000, 1488153600, 1488067200, 1487980800,
        #  1487894400, 1487808000, 1487548800 ] ],
        #  "id": 1 }
        # newer models return a dict
        if isinstance(data, list):
            self.data = {
                "clean_time": data[0],
                "clean_area": data[1],
                "clean_count": data[2],
            }
            if len(data) > 3:
                self.data["records"] = data[3]
        else:
            self.data = data

        if "records" not in self.data:
            self.data["records"] = []

    @property
    @sensor(
        "Total clean duration",
        unit="s",
        icon="mdi:timer-sand",
        device_class="duration",
        entity_category="diagnostic",
    )
    def total_duration(self) -> timedelta:
        """Total cleaning duration."""
        return pretty_seconds(self.data["clean_time"])

    @property
    @sensor(
        "Total clean area",
        unit="m²",
        icon="mdi:texture-box",
        entity_category="diagnostic",
    )
    def total_area(self) -> float:
        """Total cleaned area."""
        return pretty_area(self.data["clean_area"])

    @property
    @sensor(
        "Total clean count",
        icon="mdi:counter",
        state_class="total_increasing",
        entity_category="diagnostic",
    )
    def count(self) -> int:
        """Number of cleaning runs."""
        return int(self.data["clean_count"])

    @property
    def ids(self) -> List[int]:
        """A list of available cleaning IDs, see also
        :class:`CleaningDetails`."""
        return list(self.data["records"])

    @property
    @sensor(
        "Total dust collection count",
        icon="mdi:counter",
        state_class="total_increasing",
        entity_category="diagnostic",
    )
    def dust_collection_count(self) -> Optional[int]:
        """Total number of dust collections."""
        if "dust_collection_count" in self.data:
            return int(self.data["dust_collection_count"])
        else:
            return None


class CleaningDetails(DeviceStatus):
    """Contains details about a specific cleaning run."""

    def __init__(self, data: Union[List[Any], Dict[str, Any]]) -> None:
        # start, end, duration, area, unk, complete
        # { "result": [ [ 1488347071, 1488347123, 16, 0, 0, 0 ] ], "id": 1 }
        # newer models return a dict
        if isinstance(data, list):
            self.data = {
                "begin": data[0],
                "end": data[1],
                "duration": data[2],
                "area": data[3],
                "error": data[4],
                "complete": data[5],
            }
        else:
            self.data = data

    @property
    @sensor(
        "Last clean start",
        icon="mdi:clock-time-twelve",
        device_class="timestamp",
        entity_category="diagnostic",
    )
    def start(self) -> datetime:
        """When cleaning was started."""
        return pretty_time(self.data["begin"])

    @property
    @sensor(
        "Last clean end",
        icon="mdi:clock-time-twelve",
        device_class="timestamp",
        entity_category="diagnostic",
    )
    def end(self) -> datetime:
        """When cleaning was finished."""
        return pretty_time(self.data["end"])

    @property
    @sensor(
        "Last clean duration",
        unit="s",
        icon="mdi:timer-sand",
        device_class="duration",
        entity_category="diagnostic",
    )
    def duration(self) -> timedelta:
        """Total duration of the cleaning run."""
        return pretty_seconds(self.data["duration"])

    @property
    @sensor(
        "Last clean area",
        unit="m²",
        icon="mdi:texture-box",
        entity_category="diagnostic",
    )
    def area(self) -> float:
        """Total cleaned area."""
        return pretty_area(self.data["area"])

    @property
    def map_id(self) -> int:
        """Map id used (multi map feature) during the cleaning run."""
        return self.data.get("map_flag", 0)

    @property
    def error_code(self) -> int:
        """Error code."""
        return int(self.data["error"])

    @property
    def error(self) -> str:
        """Error state of this cleaning run."""
        return ERROR_CODES[self.data["error"]]

    @property
    def complete(self) -> bool:
        """Return True if the cleaning run was complete (e.g. without errors).

        see also :func:`error`.
        """
        return self.data["complete"] == 1


class ConsumableStatus(DeviceStatus):
    """Container for consumable status information, including information about brushes
    and duration until they should be changed. The methods returning time left are based
    on the following lifetimes:

    - Sensor cleanup time: XXX FIXME
    - Main brush: 300 hours
    - Side brush: 200 hours
    - Filter: 150 hours
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        # {'id': 1, 'result': [{'filter_work_time': 32454,
        #  'sensor_dirty_time': 3798,
        # 'side_brush_work_time': 32454,
        #  'main_brush_work_time': 32454}]}
        # TODO this should be generalized to allow different time limits
        self.data = data
        self.main_brush_total = timedelta(hours=300)
        self.side_brush_total = timedelta(hours=200)
        self.filter_total = timedelta(hours=150)
        self.sensor_dirty_total = timedelta(hours=30)

    @property
    @sensor(
        "Main brush used",
        unit="s",
        icon="mdi:brush",
        device_class="duration",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def main_brush(self) -> timedelta:
        """Main brush usage time."""
        return pretty_seconds(self.data["main_brush_work_time"])

    @property
    @sensor(
        "Main brush left",
        unit="s",
        icon="mdi:brush",
        device_class="duration",
        entity_category="diagnostic",
    )
    def main_brush_left(self) -> timedelta:
        """How long until the main brush should be changed."""
        return self.main_brush_total - self.main_brush

    @property
    @sensor(
        "Side brush used",
        unit="s",
        icon="mdi:brush",
        device_class="duration",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def side_brush(self) -> timedelta:
        """Side brush usage time."""
        return pretty_seconds(self.data["side_brush_work_time"])

    @property
    @sensor(
        "Side brush left",
        unit="s",
        icon="mdi:brush",
        device_class="duration",
        entity_category="diagnostic",
    )
    def side_brush_left(self) -> timedelta:
        """How long until the side brush should be changed."""
        return self.side_brush_total - self.side_brush

    @property
    @sensor(
        "Filter used",
        unit="s",
        icon="mdi:air-filter",
        device_class="duration",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def filter(self) -> timedelta:
        """Filter usage time."""
        return pretty_seconds(self.data["filter_work_time"])

    @property
    @sensor(
        "Filter left",
        unit="s",
        icon="mdi:air-filter",
        device_class="duration",
        entity_category="diagnostic",
    )
    def filter_left(self) -> timedelta:
        """How long until the filter should be changed."""
        return self.filter_total - self.filter

    @property
    @sensor(
        "Sensor dirty used",
        unit="s",
        icon="mdi:eye-outline",
        device_class="duration",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def sensor_dirty(self) -> timedelta:
        """Return ``sensor_dirty_time``"""
        return pretty_seconds(self.data["sensor_dirty_time"])

    @property
    @sensor(
        "Sensor dirty left",
        unit="s",
        icon="mdi:eye-outline",
        device_class="duration",
        entity_category="diagnostic",
    )
    def sensor_dirty_left(self) -> timedelta:
        return self.sensor_dirty_total - self.sensor_dirty

    @property
    @sensor(
        "Dustbin times auto-empty used",
        icon="mdi:delete",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def dustbin_auto_empty_used(self) -> Optional[int]:
        """Return ``dust_collection_work_times``"""
        if "dust_collection_work_times" in self.data:
            return self.data["dust_collection_work_times"]
        return None

    @property
    @sensor(
        "Strainer cleaned count",
        icon="mdi:air-filter",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def strainer_cleaned_count(self) -> Optional[int]:
        """Return strainer cleaned count."""
        if "strainer_work_times" in self.data:
            return self.data["strainer_work_times"]
        return None

    @property
    @sensor(
        "Cleaning brush cleaned count",
        icon="mdi:brush",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def cleaning_brush_cleaned_count(self) -> Optional[int]:
        """Return cleaning brush cleaned count."""
        if "cleaning_brush_work_times" in self.data:
            return self.data["cleaning_brush_work_times"]
        return None


class DNDStatus(DeviceStatus):
    """A container for the do-not-disturb status."""

    def __init__(self, data: Dict[str, Any]):
        # {'end_minute': 0, 'enabled': 1, 'start_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}
        self.data = data

    @property
    @sensor("Do not disturb", icon="mdi:minus-circle-off", entity_category="diagnostic")
    def enabled(self) -> bool:
        """True if DnD is enabled."""
        return bool(self.data["enabled"])

    @property
    @sensor(
        "Do not disturb start",
        icon="mdi:minus-circle-off",
        device_class="timestamp",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def start(self) -> time:
        """Start time of DnD."""
        return time(hour=self.data["start_hour"], minute=self.data["start_minute"])

    @property
    @sensor(
        "Do not disturb end",
        icon="mdi:minus-circle-off",
        device_class="timestamp",
        entity_category="diagnostic",
        enabled_default=False,
    )
    def end(self) -> time:
        """End time of DnD."""
        return time(hour=self.data["end_hour"], minute=self.data["end_minute"])


class Timer(DeviceStatus):
    """A container for scheduling.

    The timers are accessed using an integer ID, which is based on the unix timestamp of
    the creation time.
    """

    def __init__(self, data: List[Any], timezone: BaseTzInfo) -> None:
        # id / timestamp, enabled, ['<cron string>', ['command', 'params']
        # [['1488667794112', 'off', ['49 22 * * 6', ['start_clean', '']]],
        #  ['1488667777661', 'off', ['49 21 * * 3,4,5,6', ['start_clean', '']]
        # ],
        self.data = data
        self.timezone = timezone

        localized_ts = timezone.localize(self._now())

        # Initialize croniter to cause an exception on invalid entries (#847)
        self.croniter = croniter(self.cron, start_time=localized_ts)
        self._next_schedule: Optional[datetime] = None

    @property
    def id(self) -> str:
        """Unique identifier for timer.

        Usually a unix timestamp of when the timer was created, but it is not
        guaranteed. For example, valetudo apparently allows using arbitrary strings for
        this.
        """
        return self.data[0]

    @property
    def ts(self) -> Optional[datetime]:
        """Timer creation time, if the id is a unix timestamp."""
        try:
            return pretty_time(int(self.data[0]) / 1000)
        except ValueError:
            return None

    @property
    def enabled(self) -> bool:
        """True if the timer is active."""
        return self.data[1] == "on"

    @property
    def cron(self) -> str:
        """Cron-formated timer string."""
        return str(self.data[2][0])

    @property
    def action(self) -> str:
        """The action to be taken on the given time.

        Note, this seems to be always 'start'.
        """
        return str(self.data[2][1])

    @property
    def next_schedule(self) -> datetime:
        """Next schedule for the timer.

        Note, this value will not be updated after the Timer object has been created.
        """
        if self._next_schedule is None:
            self._next_schedule = self.croniter.get_next(ret_type=datetime)
        return self._next_schedule

    @staticmethod
    def _now() -> datetime:
        return datetime.now()


class SoundStatus(DeviceStatus):
    """Container for sound status."""

    def __init__(self, data):
        # {'sid_in_progress': 0, 'sid_in_use': 1004}
        self.data = data

    @property
    def current(self):
        return self.data["sid_in_use"]

    @property
    def being_installed(self):
        return self.data["sid_in_progress"]


class SoundInstallState(IntEnum):
    Unknown = 0
    Downloading = 1
    Installing = 2
    Installed = 3
    Error = 4


class SoundInstallStatus(DeviceStatus):
    """Container for sound installation status."""

    def __init__(self, data):
        # {'progress': 0, 'sid_in_progress': 0, 'state': 0, 'error': 0}
        # error 0 = no error
        # error 1 = unknown 1
        # error 2 = download error
        # error 3 = checksum error
        # error 4 = unknown 4

        self.data = data

    @property
    def state(self) -> SoundInstallState:
        """Installation state."""
        return SoundInstallState(self.data["state"])

    @property
    def progress(self) -> int:
        """Progress in percentages."""
        return self.data["progress"]

    @property
    def sid(self) -> int:
        """Sound ID for the sound being installed."""
        # this is missing on install confirmation, so let's use get
        return self.data.get("sid_in_progress")

    @property
    def error(self) -> int:
        """Error code, 0 is no error, other values unknown."""
        return self.data["error"]

    @property
    def is_installing(self) -> bool:
        """True if install is in progress."""
        return (
            self.state == SoundInstallState.Downloading
            or self.state == SoundInstallState.Installing
        )

    @property
    def is_errored(self) -> bool:
        """True if the state has an error, use `error` to access it."""
        return self.state == SoundInstallState.Error


class CarpetModeStatus(DeviceStatus):
    """Container for carpet mode status."""

    def __init__(self, data):
        # {'current_high': 500, 'enable': 1, 'current_integral': 450,
        #  'current_low': 400, 'stall_time': 10}
        self.data = data

    @property
    @sensor("Carpet mode")
    def enabled(self) -> bool:
        """True if carpet mode is enabled."""
        return self.data["enable"] == 1

    @property
    def stall_time(self) -> int:
        return self.data["stall_time"]

    @property
    def current_low(self) -> int:
        return self.data["current_low"]

    @property
    def current_high(self) -> int:
        return self.data["current_high"]

    @property
    def current_integral(self) -> int:
        return self.data["current_integral"]


class MopDryerSettings(DeviceStatus):
    """Container for mop dryer add-on."""

    def __init__(self, data: Dict[str, Any]):
        # {'status': 0, 'on': {'cliff_on': 1, 'cliff_off': 1, 'count': 10, 'dry_time': 10800},
        # 'off': {'cliff_on': 2, 'cliff_off': 1, 'count': 10}}
        self.data = data

    @property
    @setting(
        "Mop dryer enabled",
        setter_name="set_mop_dryer_enabled",
        icon="mdi:tumble-dryer",
        entity_category="config",
        enabled_default=False,
    )
    def enabled(self) -> bool:
        """Return if mop dryer is enabled."""
        return self.data["status"] == 1

    @property
    @setting(
        "Mop dry time",
        setter_name="set_mop_dryer_dry_time",
        icon="mdi:fan",
        unit="s",
        min_value=7200,
        max_value=14400,
        step=3600,
        entity_category="config",
        enabled_default=False,
    )
    def dry_time(self) -> timedelta:
        """Return mop dry time."""
        return pretty_seconds(self.data["on"]["dry_time"])
