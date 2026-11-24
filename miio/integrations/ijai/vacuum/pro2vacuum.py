import json
import logging
from datetime import time, timedelta
from enum import Enum

import click

from miio.click_common import EnumType, command, format_output
from miio.devicestatus import sensor, setting
from miio.exceptions import DeviceException
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
MI_ROBOT_VACUUM_MOP_PRO_2 = "ijai.vacuum.v3"

_MAPPINGS = {
    MI_ROBOT_VACUUM_MOP_PRO_2: {
        # Source  https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:vacuum:0000A006:ijai-v3:1
        # Robot Cleaner (siid=2)
        "state": {"siid": 2, "piid": 1},
        "error_code": {"siid": 2, "piid": 2},  # [0, 3000] step 1
        "sweep_mode": {
            "siid": 2,
            "piid": 4,
        },  # 0 - Sweep, 1 - Sweep And Mop, 2 - Mop
        "sweep_type": {
            "siid": 2,
            "piid": 8,
        },  # 0 - Global, 1 - Mop, 2 - Edge, 3 - Area, 4 - Point, 5 - Remote, 6 - Explore, 7 - Room, 8 - Floor
        "start": {"siid": 2, "aiid": 1},
        "stop": {"siid": 2, "aiid": 2},
        "start_sweep": {"siid": 2, "aiid": 3},  # Start Only Sweep
        "start_sweep_mop": {"siid": 2, "aiid": 5},  # Start Sweep Mop
        "start_mop": {"siid": 2, "aiid": 6},  # Start Mop
        "start_room_sweep": {"siid": 2, "aiid": 7},  # in: piid 10 (Room IDs, string)
        # Battery (siid=3)
        "battery": {"siid": 3, "piid": 1},  # [0, 100] step 1
        "home": {"siid": 3, "aiid": 1},  # Start Charge
        # sweep (siid=7)
        "mop_state": {"siid": 7, "piid": 4},  # 0 - none, 1 - set
        "fan_speed": {
            "siid": 7,
            "piid": 5,
        },  # 0 - off, 1 - power save, 2 - standard, 3 - turbo
        "water_level": {"siid": 7, "piid": 6},  # 0 - low, 1 - medium, 2 - high
        "side_brush_life_level": {"siid": 7, "piid": 8},  # [0, 100] step 1
        "side_brush_time_left": {"siid": 7, "piid": 9},  # [0, 180] step 1
        "main_brush_life_level": {"siid": 7, "piid": 10},  # [0, 100] step 1
        "main_brush_time_left": {"siid": 7, "piid": 11},  # [0, 360] step 1
        "filter_life_level": {"siid": 7, "piid": 12},  # [0, 100] step 1
        "filter_time_left": {"siid": 7, "piid": 13},  # [0, 180] step 1
        "mop_life_level": {"siid": 7, "piid": 14},  # [0, 100] step 1
        "mop_time_left": {"siid": 7, "piid": 15},  # [0, 180] step 1
        "current_language": {"siid": 7, "piid": 21},  # string
        "clean_time": {"siid": 7, "piid": 22},  # [0, 120] step 1
        "clean_area": {"siid": 7, "piid": 23},  # [0, 1200] step 1
        "repeat_state": {"siid": 7, "piid": 1},  # 0 - off, 1 - on (clean twice)
        "door_state": {"siid": 7, "piid": 3},  # 0 - none, 1 - dust box, 2 - water tank
        "mop_route": {"siid": 7, "piid": 7},  # 0 - bow style, 1 - Y style
        "time_zone": {"siid": 7, "piid": 20},  # [-99999, 99999] step 1
        "tank_shake": {"siid": 7, "piid": 48},  # 0 - off, 1 - on
        "shake_shift": {"siid": 7, "piid": 50},  # 1 - low, 2 - mid, 3 - high
        # Alarm (siid=4)
        "volume": {"siid": 4, "piid": 2},  # [0, 10] step 1
        # Do not disturb (siid=12)
        "dnd_enable": {"siid": 12, "piid": 1},
        "dnd_start_hour": {"siid": 12, "piid": 2},
        "dnd_start_minute": {"siid": 12, "piid": 3},
        "dnd_end_hour": {"siid": 12, "piid": 4},
        "dnd_end_minute": {"siid": 12, "piid": 5},
        # Actions
        "reset_consumable": {"siid": 7, "aiid": 1},  # in: piid 17 (consumable-index)
        "set_dnd": {"siid": 12, "aiid": 1},  # in: piids 1-6
    }
}

# Map service (siid=10), read-only access. Kept out of _MAPPINGS on purpose so
# that status() does not request these properties on every poll.
_MAP_SIID = 10
_MAP_PROPS = {
    "current_map_id": {"siid": _MAP_SIID, "piid": 2},  # uint32
    "map_count": {"siid": _MAP_SIID, "piid": 3},  # uint8 [0, 5]
    "has_new_map": {"siid": _MAP_SIID, "piid": 19},  # uint8 0 - no, 1 - yes
}
_ROOM_IDS_PIID = 10  # Robot Cleaner (siid=2) Room IDs, string
_ALARM_SIID = 4
_ALARM_PLAY_PIID = 1
_SWEEP_SIID = 7
_DIRECTION_PIID = 16
_CONSUMABLE_INDEX_PIID = 17
_MAP_AIID_GET_MAP_LIST = 1
_MAP_OUT_PIID_MAP_LIST = 4

ERROR_CODES: dict[int, str] = {2105: "Fully charged"}


def _enum_as_dict(cls):
    return {x.name: x.value for x in list(cls)}


class DeviceState(Enum):
    Sleep = 0
    Idle = 1
    Paused = 2
    GoCharging = 3
    Charging = 4
    Sweeping = 5
    SweepingAndMopping = 6
    Mopping = 7
    Upgrading = 8


class SweepMode(Enum):
    Sweep = 0
    SweepAndMop = 1
    Mop = 2


class SweepType(Enum):
    Global = 0
    Mop = 1
    Edge = 2
    Area = 3
    Point = 4
    Remote = 5
    Explore = 6
    Room = 7
    Floor = 8


class DoorState(Enum):
    Off = 0
    DustBox = 1
    WaterVolume = 2
    TwoInOneWaterVolume = 3


class FanSpeedMode(Enum):
    Off = 0
    EnergySaving = 1
    Standard = 2
    Turbo = 3


class WaterLevel(Enum):
    Low = 0
    Medium = 1
    High = 2


class MopRoute(Enum):
    BowStyle = 0
    YStyle = 1


class Direction(Enum):
    """Manual (remote control) movement, siid=7 piid=16."""

    Forward = 1
    Left = 2
    Right = 3
    Backward = 4
    Stop = 5
    Exit = 10


class Consumable(Enum):
    """Consumable index used by reset_consumable (siid=7 piid=17)."""

    MainBrush = 1
    SideBrush = 2
    Filter = 3
    Mop = 4


class TankShake(Enum):
    """Intensity of the water tank vibration (siid=7 piid=50)."""

    Low = 1
    Medium = 2
    High = 3


class Pro2Status(DeviceStatus):
    """Container for status reports from Mi Robot Vacuum-Mop 2 Pro."""

    def __init__(self, data):
        """Response (MIoT format) of a Mi Robot Vacuum-Mop 2 Pro (ijai.vacuum.v3)

        Example::
            [
                {'did': 'state', 'siid': 2, 'piid': 1, 'code': 0, 'value': 5},
                {'did': 'error_code', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
                {'did': 'sweep_mode', 'siid': 2, 'piid': 4, 'code': 0, 'value': 1},
                {'did': 'sweep_type', 'siid': 2, 'piid': 8, 'code': 0, 'value': 1},
                {'did': 'battery', 'siid': 3, 'piid': 1, 'code': 0, 'value': 100},
                {'did': 'mop_state', 'siid': 7, 'piid': 4, 'code': 0, 'value': 0},
                {'did': 'fan_speed', 'siid': 7, 'piid': 5, 'code': 0, 'value': 1},
                {'did': 'water_level', 'siid': 7, 'piid': 6, 'code': 0, 'value': 2},
                {'did': 'side_brush_life_level', 'siid': 7, 'piid': 8, 'code': 0, 'value': 0 },
                {'did': 'side_brush_time_left', 'siid': 7, 'piid': 9', 'code': 0, 'value': 0},
                {'did': 'main_brush_life_level', 'siid': 7, 'piid': 10, 'code': 0, 'value': 99},
                {'did': 'main_brush_time_left', 'siid': 7, 'piid': 11, 'code': 0, 'value': 17959},
                {'did': 'filter_life_level', 'siid': 7, 'piid': 12, 'code': 0, 'value': 0},
                {'did': 'filter_time_left', 'siid': 7, 'piid': 13, 'code': 0, 'value': 0},
                {'did': 'mop_life_level', 'siid': 7, 'piid': 14, 'code': 0, 'value': 0},
                {'did': 'mop_time_left', 'siid': 7, 'piid': 15, 'code': 0, 'value': 0},
                {'did': 'current_language', 'siid': 7, 'piid': 21, 'code': 0, 'value': 0},
                {'did': 'clean_area', 'siid': 7, 'piid': 22, 'code': 0, 'value': 0},
                {'did': 'clean_time', 'siid': 7, 'piid': 23, 'code': 0, 'value': 0},
            ]
        """
        self.data = data

    @property
    @sensor(name="Battery", unit="%", device_class="battery")
    def battery(self) -> int:
        """Battery Level."""
        return self.data["battery"]

    @property
    @sensor("Error", icon="mdi:alert")
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    @sensor("Error", icon="mdi:alert")
    def error(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        return ERROR_CODES.get(
            self.error_code, f"Unknown error code: {self.error_code}"
        )

    @property
    def state(self) -> DeviceState:
        """Vacuum Status."""
        return DeviceState(self.data["state"])

    @property
    @setting(name="Fan Speed", choices=FanSpeedMode, setter_name="set_fan_speed")
    def fan_speed(self) -> FanSpeedMode:
        """Fan Speed."""
        return FanSpeedMode(self.data["fan_speed"])

    @property
    @sensor(name="Sweep Type")
    def sweep_type(self) -> SweepType:
        """Operating Mode."""
        return SweepType(self.data["sweep_type"])

    @property
    @sensor(name="Sweep Mode")
    def sweep_mode(self) -> SweepMode:
        """Sweep Mode."""
        return SweepMode(self.data["sweep_mode"])

    @property
    @sensor("Mop Attached")
    def mop_state(self) -> bool:
        """Mop State."""
        return bool(self.data["mop_state"])

    @property
    @sensor("Water Level")
    def water_level(self) -> WaterLevel:
        """Water Level."""
        return WaterLevel(self.data["water_level"])

    @property
    @sensor("Main Brush Life Level", unit="%")
    def main_brush_life_level(self) -> int:
        """Main Brush Life Level(%)."""
        return self.data["main_brush_life_level"]

    @property
    @sensor("Main Brush Life Time Left")
    def main_brush_time_left(self) -> timedelta:
        """Main Brush Life Time Left(hours)."""
        return timedelta(hours=self.data["main_brush_time_left"])

    @property
    @sensor("Side Brush Life Level", unit="%")
    def side_brush_life_level(self) -> int:
        """Side Brush Life Level(%)."""
        return self.data["side_brush_life_level"]

    @property
    @sensor("Side Brush Life Time Left")
    def side_brush_time_left(self) -> timedelta:
        """Side Brush Life Time Left(hours)."""
        return timedelta(hours=self.data["side_brush_time_left"])

    @property
    @sensor("Filter Life Level", unit="%")
    def filter_life_level(self) -> int:
        """Filter Life Level(%)."""
        return self.data["filter_life_level"]

    @property
    @sensor("Filter Life Time Left")
    def filter_time_left(self) -> timedelta:
        """Filter Life Time Left(hours)."""
        return timedelta(hours=self.data["filter_time_left"])

    @property
    @sensor("Mop Life Level", unit="%")
    def mop_life_level(self) -> int:
        """Mop Life Level(%)."""
        return self.data["mop_life_level"]

    @property
    @sensor("Mop Life Time Left")
    def mop_time_left(self) -> timedelta:
        """Mop Life Time Left(hours)."""
        return timedelta(hours=self.data["mop_time_left"])

    @property
    @sensor("Last Clean Area", unit="m2", icon="mdi:texture-box")
    def clean_area(self) -> int:
        """Last time clean area(m^2)."""
        return self.data["clean_area"]

    @property
    @sensor("Last Clean Time", icon="mdi:timer-sand")
    def clean_time(self) -> timedelta:
        """Last time clean time(mins)."""
        return timedelta(minutes=self.data["clean_time"])

    @property
    def current_language(self) -> str:
        """Current Language."""
        return self.data["current_language"]

    @property
    @sensor("Clean Twice")
    def repeat_state(self) -> bool:
        """Whether the area is cleaned twice."""
        return bool(self.data["repeat_state"])

    @property
    @sensor("Door State")
    def door_state(self) -> DoorState:
        """Which tank (none, dust box, water tank) is attached."""
        return DoorState(self.data["door_state"])

    @property
    @sensor("Mop Route")
    def mop_route(self) -> MopRoute:
        """Mopping route."""
        return MopRoute(self.data["mop_route"])

    @property
    def time_zone(self) -> int:
        """Time zone offset configured on the device (seconds)."""
        return self.data["time_zone"]

    @property
    @sensor("Tank Shake")
    def tank_shake(self) -> bool:
        """Whether the water tank vibration is enabled."""
        return bool(self.data["tank_shake"])

    @property
    @sensor("Tank Shake Level")
    def shake_shift(self) -> TankShake:
        """Intensity of the water tank vibration."""
        return TankShake(self.data["shake_shift"])

    @property
    @sensor("Volume", unit="%")
    def volume(self) -> int:
        """Voice volume [0, 10]."""
        return self.data["volume"]

    @property
    @sensor("Do Not Disturb")
    def dnd_enabled(self) -> bool:
        """Whether do-not-disturb is enabled."""
        return bool(self.data["dnd_enable"])

    @property
    def dnd_start(self) -> time:
        """Do-not-disturb start time."""
        return time(self.data["dnd_start_hour"], self.data["dnd_start_minute"])

    @property
    def dnd_end(self) -> time:
        """Do-not-disturb end time."""
        return time(self.data["dnd_end_hour"], self.data["dnd_end_minute"])


class Pro2MapStatus(DeviceStatus):
    """Container for the map information of a Mi Robot Vacuum-Mop 2 Pro."""

    def __init__(self, data):
        """Response (MIoT format) of the map service (siid=10)

        Example::
            [
                {'did': 'current_map_id', 'siid': 10, 'piid': 2, 'code': 0, 'value': 1700000002},
                {'did': 'map_count', 'siid': 10, 'piid': 3, 'code': 0, 'value': 4},
                {'did': 'has_new_map', 'siid': 10, 'piid': 19, 'code': 0, 'value': 0},
            ]
        """
        self.data = data

    @property
    def current_map_id(self) -> int:
        """Id of the currently active map."""
        return self.data["current_map_id"]

    @property
    def map_count(self) -> int:
        """Number of stored maps."""
        return self.data["map_count"]

    @property
    def has_new_map(self) -> bool:
        """True if the device has a map that was not uploaded yet."""
        return bool(self.data["has_new_map"])


class Pro2Vacuum(MiotDevice):
    """Support for Mi Robot Vacuum-Mop 2 Pro (ijai.vacuum.v3)."""

    _mappings = _MAPPINGS

    @command()
    def status(self) -> Pro2Status:
        """Retrieve properties."""
        return Pro2Status(
            {
                # max_properties limited to 10 to avoid "Checksum error"
                # messages from the device.
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping(max_properties=10)
            }
        )

    @command()
    def map_status(self) -> Pro2MapStatus:
        """Return the current map id, the number of maps and the new-map flag."""
        props = [{"did": k, **v} for k, v in _MAP_PROPS.items()]
        return Pro2MapStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties(
                    props, property_getter="get_properties", max_properties=10
                )
            }
        )

    @command()
    def get_maps(self) -> list[dict]:
        """Return the stored maps as a list of dicts with name, id and cur keys.

        ``cur`` is true for the map that is currently active.
        """
        res = self.call_action_by(_MAP_SIID, _MAP_AIID_GET_MAP_LIST)
        for out in res.get("out", []):
            if out.get("piid") == _MAP_OUT_PIID_MAP_LIST:
                return json.loads(out["value"])
        raise DeviceException(f"Unexpected response to get-map-list: {res}")

    @command()
    def home(self):
        """Go Home."""
        return self.call_action_from_mapping("home")

    @command()
    def start(self) -> None:
        """Start Cleaning."""
        return self.call_action_from_mapping("start")

    @command()
    def stop(self):
        """Stop Cleaning."""
        return self.call_action_from_mapping("stop")

    @command()
    def start_sweep(self) -> None:
        """Start cleaning in sweep-only mode."""
        return self.call_action_from_mapping("start_sweep")

    @command()
    def start_sweep_mop(self) -> None:
        """Start cleaning in sweep-and-mop mode."""
        return self.call_action_from_mapping("start_sweep_mop")

    @command()
    def start_mop(self) -> None:
        """Start cleaning in mop-only mode."""
        return self.call_action_from_mapping("start_mop")

    @command(click.argument("room_ids", type=int, nargs=-1, required=True))
    def start_rooms(self, room_ids: list[int]) -> None:
        """Start cleaning the given rooms.

        Room ids are the ones used by the map of the device (e.g. 10, 11, ...).
        """
        if not room_ids:
            raise ValueError("At least one room id is required")
        rooms = ",".join(str(int(r)) for r in room_ids)
        return self.call_action_from_mapping(
            "start_room_sweep", [{"piid": _ROOM_IDS_PIID, "value": rooms}]
        )

    @command(
        click.argument("fan_speed", type=EnumType(FanSpeedMode)),
        default_output=format_output("Setting fan speed to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: FanSpeedMode):
        """Set fan speed."""
        return self.set_property("fan_speed", fan_speed)

    @command()
    def fan_speed_presets(self) -> dict[str, int]:
        """Return available fan speed presets."""
        return _enum_as_dict(FanSpeedMode)

    @command(click.argument("speed", type=int))
    def set_fan_speed_preset(self, speed_preset: int) -> None:
        """Set fan speed preset speed."""
        if speed_preset not in self.fan_speed_presets().values():
            raise ValueError(
                f"Invalid preset speed {speed_preset}, not in: {self.fan_speed_presets().values()}"
            )
        return self.set_property("fan_speed", speed_preset)

    @command(
        click.argument("sweep_mode", type=EnumType(SweepMode)),
        default_output=format_output("Setting sweep mode to {sweep_mode}"),
    )
    def set_sweep_mode(self, sweep_mode: SweepMode):
        """Set the sweep mode (sweep, sweep and mop, mop)."""
        return self.set_property("sweep_mode", sweep_mode.value)

    @command(
        click.argument("water_level", type=EnumType(WaterLevel)),
        default_output=format_output("Setting water level to {water_level}"),
    )
    def set_water_level(self, water_level: WaterLevel):
        """Set the water level used when mopping."""
        return self.set_property("water_level", water_level.value)

    @command(
        click.argument("mop_route", type=EnumType(MopRoute)),
        default_output=format_output("Setting mop route to {mop_route}"),
    )
    def set_mop_route(self, mop_route: MopRoute):
        """Set the mopping route (bow style or Y style)."""
        return self.set_property("mop_route", mop_route.value)

    @command(click.argument("enable", type=bool))
    def set_repeat(self, enable: bool):
        """Enable or disable cleaning the area twice."""
        return self.set_property("repeat_state", int(enable))

    @command(click.argument("enable", type=bool))
    def set_tank_shake(self, enable: bool):
        """Enable or disable the water tank vibration."""
        return self.set_property("tank_shake", int(enable))

    @command(click.argument("level", type=EnumType(TankShake)))
    def set_tank_shake_level(self, level: TankShake):
        """Set the intensity of the water tank vibration."""
        return self.set_property("shake_shift", level.value)

    @command(click.argument("volume", type=click.IntRange(0, 10)))
    def set_volume(self, volume: int):
        """Set the voice volume [0, 10]."""
        return self.set_property("volume", volume)

    @command()
    def locate(self):
        """Play the "I am here" sound (siid=4 piid=1)."""
        return self.set_property_by(_ALARM_SIID, _ALARM_PLAY_PIID, 1)

    @command(click.argument("consumable", type=EnumType(Consumable)))
    def reset_consumable(self, consumable: Consumable):
        """Reset the lifetime counter of a consumable."""
        return self.call_action_from_mapping(
            "reset_consumable",
            [{"piid": _CONSUMABLE_INDEX_PIID, "value": consumable.value}],
        )

    @command(
        click.argument("enable", type=bool),
        click.argument("start", type=click.DateTime(["%H:%M"]), required=False),
        click.argument("end", type=click.DateTime(["%H:%M"]), required=False),
    )
    def set_dnd(self, enable: bool, start=None, end=None):
        """Configure do-not-disturb.

        ``start`` and ``end`` are ``datetime.time`` (or ``HH:MM`` on the CLI). If they
        are omitted, the currently configured times are kept.
        """
        status = self.status()
        start = start.time() if hasattr(start, "time") else start
        end = end.time() if hasattr(end, "time") else end
        start = start or status.dnd_start
        end = end or status.dnd_end
        return self.call_action_from_mapping(
            "set_dnd",
            [
                {"piid": 1, "value": int(enable)},
                {"piid": 2, "value": start.hour},
                {"piid": 3, "value": start.minute},
                {"piid": 4, "value": end.hour},
                {"piid": 5, "value": end.minute},
                {"piid": 6, "value": status.time_zone},
            ],
        )

    @command(click.argument("direction", type=EnumType(Direction)))
    def manual_control(self, direction: Direction):
        """Move the robot manually (remote control mode).

        Send ``Direction.Exit`` to leave the manual mode.
        """
        return self.set_property_by(_SWEEP_SIID, _DIRECTION_PIID, direction.value)
