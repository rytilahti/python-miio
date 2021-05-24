"""Viomi Vacuum.

# https://github.com/rytilahti/python-miio/issues/550#issuecomment-552780952
# https://github.com/homebridge-xiaomi-roborock-vacuum/homebridge-xiaomi-roborock-vacuum/blob/ee10cbb3e98dba75d9c97791a6e1fcafc1281591/miio/lib/devices/vacuum.js
# https://github.com/homebridge-xiaomi-roborock-vacuum/homebridge-xiaomi-roborock-vacuum/blob/ee10cbb3e98dba75d9c97791a6e1fcafc1281591/miio/lib/devices/viomivacuum.js

Features:

Main:
- Area/Duration - Missing (get_clean_summary/get_clean_record
- Battery - battery_life
- Dock - set_charge
- Start/Pause - set_mode_withroom
- Modes (Vacuum/Vacuum&Mop/Mop) - set_mop/id_mop
- Fan Speed (Silent/Standard/Medium/Turbo) - set_suction/suction_grade
- Water Level (Low/Medium/High) - set_suction/water_grade

Settings:
- Cleaning history - MISSING (cleanRecord)
- Scheduled cleanup - get_ordertime
- Vacuum along the edges - get_mode/set_mode
- Secondary cleanup - set_repeat/repeat_cleaning
- Mop or vacuum & mod mode - set_moproute/mop_route
- DND(DoNotDisturb) - set_notdisturb/get_notdisturb
- Voice On/Off - set_sound_volume/sound_volume
- Remember Map - remember_map
- Virtual wall/restricted area - MISSING
- Map list - get_maps/rename_map/delete_map/set_map
- Area editor - MISSING
- Reset map - MISSING
- Device leveling - MISSING
- Looking for the vacuum-mop - MISSING (find_me)
- Consumables statistics - get_properties
- Remote Control - MISSING

Misc:
- Get Properties
- Language - set_language
- Led - set_light
- Rooms - get_ordertime (hack)
- Clean History Path - MISSING (historyPath)
- Map plan - MISSING (map_plan)
"""
import itertools
import logging
import time
from collections import defaultdict
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException
from .utils import pretty_seconds
from .vacuumcontainers import ConsumableStatus, DNDStatus

_LOGGER = logging.getLogger(__name__)


ERROR_CODES = {
    0: "Sleeping and not charging",
    500: "Radar timed out",
    501: "Wheels stuck",
    502: "Low battery",
    503: "Dust bin missing",
    508: "Uneven ground",
    509: "Cliff sensor error",
    510: "Collision sensor error",
    511: "Could not return to dock",
    512: "Could not return to dock",
    513: "Could not navigate",
    514: "Vacuum stuck",
    515: "Charging error",
    516: "Mop temperature error",
    521: "Water tank is not installed",
    522: "Mop is not installed",
    525: "Insufficient water in water tank",
    527: "Remove mop",
    528: "Dust bin missing",
    529: "Mop and water tank missing",
    530: "Mop and water tank missing",
    531: "Water tank is not installed",
    2101: "Unsufficient battery, continuing cleaning after recharge",
    2103: "Charging",
    2105: "Fully charged",
}


class ViomiVacuumException(DeviceException):
    """Exception raised by Viomi Vacuum."""


class ViomiPositionPoint:
    """Vacuum position coordinate."""

    def __init__(self, pos_x, pos_y, phi, update, plan_multiplicator=1):
        self._pos_x = pos_x
        self._pos_y = pos_y
        self.phi = phi
        self.update = update
        self._plan_multiplicator = plan_multiplicator

    @property
    def pos_x(self):
        """X coordinate with multiplicator."""
        return self._pos_x * self._plan_multiplicator

    @property
    def pos_y(self):
        """Y coordinate with multiplicator."""
        return self._pos_y * self._plan_multiplicator

    def image_pos_x(self, offset, img_center):
        """X coordinate on an image."""
        return self.pos_x - offset + img_center

    def image_pos_y(self, offset, img_center):
        """Y coordinate on an image."""
        return self.pos_y - offset + img_center

    def __repr__(self) -> str:
        return "<ViomiPositionPoint x: {}, y: {}, phi: {}, update {}>".format(
            self.pos_x, self.pos_y, self.phi, self.update
        )

    def __eq__(self, value) -> bool:
        return (
            self.pos_x == value.pos_x
            and self.pos_y == value.pos_y
            and self.phi == value.phi
        )


class ViomiConsumableStatus(ConsumableStatus):
    """Consumable container for viomi vacuums.

    Note that this exposes `mop` and `mop_left` that are not available in the base
    class, while returning zeroed timedeltas for `sensor_dirty` and `sensor_dirty_left`
    which it doesn't report.
    """

    def __init__(self, data: List[int]) -> None:
        # [17, 17, 17, 17]
        self.data = {
            "main_brush_work_time": data[0] * 60 * 60,
            "side_brush_work_time": data[1] * 60 * 60,
            "filter_work_time": data[2] * 60 * 60,
            "mop_dirty_time": data[3] * 60 * 60,
        }
        self.side_brush_total = timedelta(hours=180)
        self.main_brush_total = timedelta(hours=360)
        self.filter_total = timedelta(hours=180)
        self.mop_total = timedelta(hours=180)
        self.sensor_dirty_total = timedelta(seconds=0)

    @property
    def mop(self) -> timedelta:
        """Return ``sensor_dirty_time``"""
        return pretty_seconds(self.data["mop_dirty_time"])

    @property
    def mop_left(self) -> timedelta:
        """How long until the mop should be changed."""
        return self.mop_total - self.mop

    @property
    def sensor_dirty(self) -> timedelta:
        """Viomi has no sensor dirty, so we return zero here."""
        return timedelta(seconds=0)

    @property
    def sensor_dirty_left(self) -> timedelta:
        """Viomi has no sensor dirty, so we return zero here."""
        return self.sensor_dirty_total - self.sensor_dirty


class ViomiVacuumSpeed(Enum):
    Silent = 0
    Standard = 1
    Medium = 2
    Turbo = 3


class ViomiVacuumState(Enum):
    Unknown = -1
    IdleNotDocked = 0
    Idle = 1
    Idle2 = 2
    Cleaning = 3
    Returning = 4
    Docked = 5
    VacuumingAndMopping = 6


class ViomiMode(Enum):
    Vacuum = 0  # No Mop, Vacuum only
    VacuumAndMop = 1
    Mop = 2
    CleanZone = 3
    CleanSpot = 4


class ViomiLanguage(Enum):
    CN = 1  # Chinese (default)
    EN = 2  # English


class ViomiLedState(Enum):
    Off = 0
    On = 1


class ViomiCarpetTurbo(Enum):
    Off = 0
    Medium = 1
    Turbo = 2


class ViomiMovementDirection(Enum):
    Forward = 1
    Left = 2  # Rotate
    Right = 3  # Rotate
    Backward = 4
    Stop = 5
    Unknown = 10


class ViomiBinType(Enum):
    Vacuum = 1
    Water = 2
    VacuumAndWater = 3
    NoBin = 0


class ViomiWaterGrade(Enum):
    Low = 11
    Medium = 12
    High = 13


class ViomiRoutePattern(Enum):
    """Mopping pattern."""

    S = 0
    Y = 1


class ViomiEdgeState(Enum):
    Off = 0
    Unknown = 1
    On = 2
    # NOTE: When I got 5, the device was super slow
    # Shutdown and restart device fixed the issue
    Unknown2 = 5


class ViomiVacuumStatus(DeviceStatus):
    def __init__(self, data):
        # ["run_state","mode","err_state","battary_life","box_type","mop_type","s_time","s_area",
        # "suction_grade","water_grade","remember_map","has_map","is_mop","has_newmap"]'
        # 1,               11,           1,            1,         1,       0          ]
        self.data = data

    @property
    def state(self):
        """State of the vacuum."""
        try:
            return ViomiVacuumState(self.data["run_state"])
        except ValueError:
            _LOGGER.warning("Unknown vacuum state: %s", self.data["run_state"])
            return ViomiVacuumState.Unknown

    @property
    def edge_state(self) -> ViomiEdgeState:
        """Vaccum along the edges.

        The settings is valid once
        0: Off
        1: Unknown
        2: On
        5: Unknown
        """
        return ViomiEdgeState(self.data["mode"])

    @property
    def mop_installed(self) -> bool:
        """True if the mop is installed."""
        return bool(self.data["mop_type"])

    @property
    def error_code(self) -> int:
        """Error code from vacuum."""
        return self.data["err_state"]

    @property
    def error(self) -> Optional[str]:
        """String presentation for the error code."""
        if self.error_code is None:
            return None

        return ERROR_CODES.get(self.error_code, f"Unknown error {self.error_code}")

    @property
    def battery(self) -> int:
        """Battery in percentage."""
        return self.data["battary_life"]

    @property
    def bin_type(self) -> ViomiBinType:
        """Type of the inserted bin."""
        return ViomiBinType(self.data["box_type"])

    @property
    def clean_time(self) -> timedelta:
        """Cleaning time."""
        return pretty_seconds(self.data["s_time"] * 60)

    @property
    def clean_area(self) -> float:
        """Cleaned area in square meters."""
        return self.data["s_area"]

    @property
    def fanspeed(self) -> ViomiVacuumSpeed:
        """Current fan speed."""
        return ViomiVacuumSpeed(self.data["suction_grade"])

    @command()
    def fan_speed_presets(self) -> Dict[str, int]:
        """Return dictionary containing supported fanspeeds."""
        return {x.name: x.value for x in list(ViomiVacuumSpeed)}

    @property
    def water_grade(self) -> ViomiWaterGrade:
        """Water grade."""
        return ViomiWaterGrade(self.data["water_grade"])

    @property
    def remember_map(self) -> bool:
        """True to remember the map."""
        return bool(self.data["remember_map"])

    @property
    def has_map(self) -> bool:
        """True if device has map?"""
        return bool(self.data["has_map"])

    @property
    def has_new_map(self) -> bool:
        """True if the device has scanned a new map (like a new floor)."""
        return bool(self.data["has_newmap"])

    @property
    def mop_mode(self) -> ViomiMode:
        """Whether mopping is enabled and if so which mode."""
        return ViomiMode(self.data["is_mop"])

    @property
    def current_map_id(self) -> float:
        """Current map id."""
        return self.data["cur_mapid"]

    @property
    def hw_info(self) -> str:
        """Hardware info."""
        return self.data["hw_info"]

    @property
    def charging(self) -> bool:
        """True if battery is charging.

        Note: When the battery is at 100%, device reports that it is not charging.
        """
        return not bool(self.data["is_charge"])

    @property
    def is_on(self) -> bool:
        """True if device is working."""
        return not bool(self.data["is_work"])

    @property
    def light_state(self) -> bool:
        """Led state.

        This seems doing nothing on STYJ02YM
        """
        return bool(self.data["light_state"])

    @property
    def map_number(self) -> int:
        """Number of saved maps."""
        return self.data["map_num"]

    @property
    def mop_route(self) -> ViomiRoutePattern:
        """Pattern mode."""
        return ViomiRoutePattern(self.data["mop_route"])

    # @property
    # def order_time(self) -> int:
    #    """FIXME: ??? int or bool."""
    #    return self.data["order_time"]

    @property
    def repeat_cleaning(self) -> bool:
        """Secondary clean up state.

        True if the cleaning is performed twice
        """
        return self.data["repeat_state"]

    # @property
    # def start_time(self) -> int:
    #    """FIXME: ??? int or bool."""
    #    return self.data["start_time"]

    @property
    def sound_volume(self) -> int:
        """Voice volume level (from 0 to 100%, 0 means Off)."""
        return self.data["v_state"]

    # @property
    # def water_percent(self) -> int:
    #    """FIXME: ??? int or bool."""
    #    return self.data["water_percent"]

    # @property
    # def zone_data(self) -> int:
    #    """FIXME: ??? int or bool."""
    #    return self.data["zone_data"]


def _get_rooms_from_schedules(schedules: List[str]) -> Tuple[bool, Dict]:
    """Read the result of "get_ordertime" command to extract room names and ids.

    The `schedules` input needs to follow the following format
    * ['1_0_32_0_0_0_1_1_11_0_1594139992_2_11_room1_13_room2', ...]
    * [Id_Enabled_Repeatdays_Hour_Minute_?_? _?_?_?_?_NbOfRooms_RoomId_RoomName_RoomId_RoomName_..., ...]

    The function parse get_ordertime output to find room names and ids
    To use this function you need:
    1. to create a scheduled cleanup with the following properties:
    * Hour: 00
    * Minute: 00
    * Select all (minus one) the rooms one by one
    * Set as inactive scheduled cleanup
    2. then to create an other scheduled cleanup with the room missed at
       previous step with the following properties:
    * Hour: 00
    * Minute: 00
    * Select only the missed room
    * Set as inactive scheduled cleanup

    More information:
    * https://github.com/homebridge-xiaomi-roborock-vacuum/homebridge-xiaomi-roborock-vacuum/blob/d73925c0106984a995d290e91a5ba4fcfe0b6444/index.js#L969
    * https://github.com/homebridge-xiaomi-roborock-vacuum/homebridge-xiaomi-roborock-vacuum#semi-automatic
    """
    rooms = {}
    scheduled_found = False
    for raw_schedule in schedules:
        schedule = raw_schedule.split("_")
        # Scheduled cleanup needs to be scheduled for 00:00 and inactive
        if schedule[1] == "0" and schedule[3] == "0" and schedule[4] == "0":
            scheduled_found = True
            raw_rooms = schedule[12:]
            rooms_iter = iter(raw_rooms)
            rooms.update(
                dict(itertools.zip_longest(rooms_iter, rooms_iter, fillvalue=None))
            )
    return scheduled_found, rooms


class ViomiVacuum(Device):
    """Interface for Viomi vacuums (viomi.vacuum.v7)."""

    timeout = 5
    retry_count = 10

    def __init__(
        self, ip: str, token: str = None, start_id: int = 0, debug: int = 0
    ) -> None:
        super().__init__(ip, token, start_id, debug)
        self.manual_seqnum = -1
        self._cache: Dict[str, Any] = {"edge_state": None, "rooms": {}, "maps": {}}

    @command(
        default_output=format_output(
            "\n",
            "General\n"
            "=======\n\n"
            "Hardware version: {result.hw_info}\n"
            "State: {result.state}\n"
            "Working: {result.is_on}\n"
            "Battery status: {result.error}\n"
            "Battery: {result.battery}\n"
            "Charging: {result.charging}\n"
            "Box type: {result.bin_type}\n"
            "Fan speed: {result.fanspeed}\n"
            "Water grade: {result.water_grade}\n"
            "Mop mode: {result.mop_mode}\n"
            "Mop installed: {result.mop_installed}\n"
            "Vacuum along the edges: {result.edge_state}\n"
            "Mop route pattern: {result.mop_route}\n"
            "Secondary Cleanup: {result.repeat_cleaning}\n"
            "Sound Volume: {result.sound_volume}\n"
            "Clean time: {result.clean_time}\n"
            "Clean area: {result.clean_area} m²\n"
            "\n"
            "Map\n"
            "===\n\n"
            "Current map ID: {result.current_map_id}\n"
            "Remember map: {result.remember_map}\n"
            "Has map: {result.has_map}\n"
            "Has new map: {result.has_new_map}\n"
            "Number of maps: {result.map_number}\n"
            "\n"
            "Unknown properties\n"
            "=================\n\n"
            "Light state: {result.light_state}\n"
            # "Order time: {result.order_time}\n"
            # "Start time: {result.start_time}\n"
            # "water_percent: {result.water_percent}\n"
            # "zone_data: {result.zone_data}\n",
        )
    )
    def status(self) -> ViomiVacuumStatus:
        """Retrieve properties."""
        properties = [
            "battary_life",
            "box_type",
            "cur_mapid",
            "err_state",
            "has_map",
            "has_newmap",
            "hw_info",
            "is_charge",
            "is_mop",
            "is_work",
            "light_state",
            "map_num",
            "mode",
            "mop_route",
            "mop_type",
            "remember_map",
            "repeat_state",
            "run_state",
            "s_area",
            "s_time",
            "suction_grade",
            "v_state",
            "water_grade",
            # The following list of properties existing but
            # there are not used in the code
            # "order_time",
            # "start_time",
            # "water_percent",
            # "zone_data",
            # "sw_info",
            # "main_brush_hours",
            # "main_brush_life",
            # "side_brush_hours",
            # "side_brush_life",
            # "mop_hours",
            # "mop_life",
            # "hypa_hours",
            # "hypa_life",
        ]

        values = self.get_properties(properties)

        return ViomiVacuumStatus(defaultdict(lambda: None, zip(properties, values)))

    @command()
    def home(self):
        """Return to home."""
        self.send("set_charge", [1])

    @command()
    def start(self):
        """Start cleaning."""
        # params: [edge, 1, roomIds.length, *list_of_room_ids]
        # - edge: see ViomiEdgeState
        # - 1: start cleaning (2 pause, 0 stop)
        # - roomIds.length
        # - *room_id_list
        # 3rd param of set_mode_withroom is room_array_len and next are
        # room ids ([0, 1, 3, 11, 12, 13] = start cleaning rooms 11-13).
        # room ids are encoded in map and it's part of cloud api so best way
        # to get it is log between device <> mi home app
        # (before map format is supported).
        self._cache["edge_state"] = self.get_properties(["mode"])
        self.send("set_mode_withroom", self._cache["edge_state"] + [1, 0])

    @command(
        click.option(
            "--rooms",
            "-r",
            multiple=True,
            help="Rooms name or room id. Can be used multiple times",
        )
    )
    def start_with_room(self, rooms):
        """Start cleaning specific rooms."""
        if not self._cache["rooms"]:
            self.get_rooms()
        reverse_rooms = {v: k for k, v in self._cache["rooms"].items()}
        room_ids = []
        for room in rooms:
            if room in self._cache["rooms"]:
                room_ids.append(int(room))
            elif room in reverse_rooms:
                room_ids.append(int(reverse_rooms[room]))
            else:
                room_keys = ", ".join(self._cache["rooms"].keys())
                room_ids = ", ".join(self._cache["rooms"].values())
                raise DeviceException(
                    f"Room {room} is unknown, it must be in {room_keys} or {room_ids}"
                )

        self._cache["edge_state"] = self.get_properties(["mode"])
        self.send(
            "set_mode_withroom",
            self._cache["edge_state"] + [1, len(room_ids)] + room_ids,
        )

    @command()
    def pause(self):
        """Pause cleaning."""
        # params: [edge_state, 0]
        # - edge: see ViomiEdgeState
        # - 2: pause cleaning
        if not self._cache["edge_state"]:
            self._cache["edge_state"] = self.get_properties(["mode"])
        self.send("set_mode", self._cache["edge_state"] + [2])

    @command()
    def stop(self):
        """Validate that Stop cleaning."""
        # params: [edge_state, 0]
        # - edge: see ViomiEdgeState
        # - 0: stop cleaning
        if not self._cache["edge_state"]:
            self._cache["edge_state"] = self.get_properties(["mode"])
        self.send("set_mode", self._cache["edge_state"] + [0])

    @command(click.argument("mode", type=EnumType(ViomiMode)))
    def clean_mode(self, mode: ViomiMode):
        """Set the cleaning mode.

        [vacuum, vacuumAndMop, mop, cleanzone, cleanspot]
        """
        self.send("set_mop", [mode.value])

    @command(click.argument("speed", type=EnumType(ViomiVacuumSpeed)))
    def set_fan_speed(self, speed: ViomiVacuumSpeed):
        """Set fanspeed [silent, standard, medium, turbo]."""
        self.send("set_suction", [speed.value])

    @command(click.argument("watergrade", type=EnumType(ViomiWaterGrade)))
    def set_water_grade(self, watergrade: ViomiWaterGrade):
        """Set water grade.

        [low, medium, high]
        """
        self.send("set_suction", [watergrade.value])

    def get_positions(self, plan_multiplicator=1) -> List[ViomiPositionPoint]:
        """Return the last positions.

        plan_multiplicator scale up the coordinates values
        """
        results = self.send("get_curpos", [])
        positions = []
        # Group result 4 by 4
        for res in [i for i in zip(*(results[i::4] for i in range(4)))]:
            # ignore type require for mypy error
            # "ViomiPositionPoint" gets multiple values for keyword argument "plan_multiplicator"
            positions.append(
                ViomiPositionPoint(*res, plan_multiplicator=plan_multiplicator)  # type: ignore
            )
        return positions

    @command()
    def get_current_position(self) -> Optional[ViomiPositionPoint]:
        """Return the current position."""
        positions = self.get_positions()
        if positions:
            return positions[-1]
        return None

    # MISSING cleaning history

    @command()
    def get_scheduled_cleanup(self):
        """Not implemented yet."""
        # Needs to reads and understand the return of:
        # self.send("get_ordertime", [])
        # [id, enabled, repeatdays, hour, minute, ?, ? , ?, ?, ?, ?, nb_of_rooms, room_id, room_name, room_id, room_name, ...]
        raise NotImplementedError()

    @command()
    def add_timer(self):
        """Not implemented yet."""
        # Needs to reads and understand:
        # self.send("set_ordertime", [????])
        raise NotImplementedError()

    @command()
    def delete_timer(self):
        """Not implemented yet."""
        # Needs to reads and understand:
        # self.send("det_ordertime", [shedule_id])
        raise NotImplementedError()

    @command(click.argument("state", type=EnumType(ViomiEdgeState)))
    def set_edge(self, state: ViomiEdgeState):
        """Vacuum along edges.

        This is valid for a single cleaning.
        """
        return self.send("set_mode", [state.value])

    @command(click.argument("state", type=bool))
    def set_repeat(self, state: bool):
        """Set or Unset repeat mode (Secondary cleanup)."""
        return self.send("set_repeat", [int(state)])

    @command(click.argument("mop_mode", type=EnumType(ViomiRoutePattern)))
    def set_route_pattern(self, mop_mode: ViomiRoutePattern):
        """Set the mop route pattern."""
        self.send("set_moproute", [mop_mode.value])

    @command()
    def dnd_status(self):
        """Returns do-not-disturb status."""
        status = self.send("get_notdisturb")
        return DNDStatus(
            dict(
                enabled=status[0],
                start_hour=status[1],
                start_minute=status[2],
                end_hour=status[3],
                end_minute=status[4],
            )
        )

    @command(
        click.option("--disable", is_flag=True),
        click.argument("start_hr", type=int),
        click.argument("start_min", type=int),
        click.argument("end_hr", type=int),
        click.argument("end_min", type=int),
    )
    def set_dnd(
        self, disable: bool, start_hr: int, start_min: int, end_hr: int, end_min: int
    ):
        """Set do-not-disturb.

        :param int start_hr: Start hour
        :param int start_min: Start minute
        :param int end_hr: End hour
        :param int end_min: End minute
        """
        return self.send(
            "set_notdisturb",
            [0 if disable else 1, start_hr, start_min, end_hr, end_min],
        )

    @command(click.argument("volume", type=click.IntRange(0, 10)))
    def set_sound_volume(self, volume: int):
        """Switch the voice on or off."""
        enabled = 1
        if volume == 0:
            enabled = 0
        return self.send("set_voice", [enabled, volume])

    @command(click.argument("state", type=bool))
    def set_remember_map(self, state: bool):
        """Set remember map state."""
        return self.send("set_remember", [int(state)])

    # MISSING: Virtual wall/restricted area

    @command()
    def get_maps(self) -> List[Dict[str, Any]]:
        """Return map list.

        [{'name': 'MapName1', 'id': 1598622255, 'cur': False},
         {'name': 'MapName2', 'id': 1599508355, 'cur': True},
          ...]
        """
        if not self._cache["maps"]:
            self._cache["maps"] = self.send("get_map")
        return self._cache["maps"]

    @command(click.argument("map_id", type=int))
    def set_map(self, map_id: int):
        """Change current map."""
        maps = self.get_maps()
        if map_id not in [m["id"] for m in maps]:
            raise ViomiVacuumException("Map id {} doesn't exists".format(map_id))
        return self.send("set_map", [map_id])

    @command(click.argument("map_id", type=int))
    def delete_map(self, map_id: int):
        """Delete map."""
        maps = self.get_maps()
        if map_id not in [m["id"] for m in maps]:
            raise ViomiVacuumException("Map id {} doesn't exists".format(map_id))
        return self.send("del_map", [map_id])

    @command(
        click.argument("map_id", type=int),
        click.argument("map_name", type=str),
    )
    def rename_map(self, map_id: int, map_name: str):
        """Rename map."""
        maps = self.get_maps()
        if map_id not in [m["id"] for m in maps]:
            raise ViomiVacuumException(f"Map id {map_id} doesn't exists")
        return self.send("rename_map", {"mapID": map_id, "name": map_name})

    @command(
        click.option("--map-id", type=int, default=None),
        click.option("--map-name", type=str, default=None),
        click.option("--refresh", type=bool, default=False),
    )
    def get_rooms(
        self, map_id: int = None, map_name: str = None, refresh: bool = False
    ):
        """Return room ids and names."""
        if self._cache["rooms"] and not refresh:
            return self._cache["rooms"]

        # TODO: map_name and map_id are just dead code here?
        if map_name:
            maps = self.get_maps()
            map_ids = [map_["id"] for map_ in maps if map_["name"] == map_name]
            if not map_ids:
                map_names = ", ".join([m["name"] for m in maps])
                raise ViomiVacuumException(
                    f"Error: Bad map name, should be in {map_names}"
                )
        elif map_id:
            maps = self.get_maps()
            if map_id not in [m["id"] for m in maps]:
                map_ids_str = ", ".join([str(m["id"]) for m in maps])
                raise ViomiVacuumException(
                    f"Error: Bad map id, should be in {map_ids_str}"
                )
        # Get scheduled cleanup
        schedules = self.send("get_ordertime", [])
        scheduled_found, rooms = _get_rooms_from_schedules(schedules)
        if not scheduled_found:
            msg = (
                "Fake schedule not found. "
                "Please create a scheduled cleanup with the "
                "following properties:\n"
                "* Hour: 00\n"
                "* Minute: 00\n"
                "* Select all (minus one) the rooms one by one\n"
                "* Set as inactive scheduled cleanup\n"
                "Then create a scheduled cleanup with the room missed at "
                "previous step with the following properties:\n"
                "* Hour: 00\n"
                "* Minute: 00\n"
                "* Select only the missed room\n"
                "* Set as inactive scheduled cleanup\n"
            )
            raise ViomiVacuumException(msg)

        self._cache["rooms"] = rooms
        return rooms

    # MISSING Area editor

    # MISSING Reset map

    # MISSING Device leveling

    # MISSING Looking for the vacuum-mop

    @command()
    def consumable_status(self) -> ViomiConsumableStatus:
        """Return information about consumables."""
        return ViomiConsumableStatus(self.send("get_consumables"))

    @command(
        click.argument("direction", type=EnumType(ViomiMovementDirection)),
        click.option(
            "--duration",
            type=float,
            default=0.5,
            help="number of seconds to perform this movement",
        ),
    )
    def move(self, direction: ViomiMovementDirection, duration=0.5):
        """Manual movement."""
        start = time.time()
        while time.time() - start < duration:
            self.send("set_direction", [direction.value])
            time.sleep(0.1)
        self.send("set_direction", [ViomiMovementDirection.Stop.value])

    @command(click.argument("language", type=EnumType(ViomiLanguage)))
    def set_language(self, language: ViomiLanguage):
        """Set the device's audio language.

        This seems doing nothing on STYJ02YM
        """
        return self.send("set_language", [language.value])

    @command(click.argument("state", type=EnumType(ViomiLedState)))
    def led(self, state: ViomiLedState):
        """Switch the button leds on or off.

        This seems doing nothing on STYJ02YM
        """
        return self.send("set_light", [state.value])

    @command(click.argument("mode", type=EnumType(ViomiCarpetTurbo)))
    def carpet_mode(self, mode: ViomiCarpetTurbo):
        """Set the carpet mode.

        This seems doing nothing on STYJ02YM
        """
        return self.send("set_carpetturbo", [mode.value])
