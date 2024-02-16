import logging
from datetime import timedelta
from enum import Enum
from typing import Dict

import click

from miio.click_common import EnumType, command, format_output
from miio.devicestatus import sensor, setting
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
    }
}

ERROR_CODES: Dict[int, str] = {2105: "Fully charged"}


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

    @command(
        click.argument("fan_speed", type=EnumType(FanSpeedMode)),
        default_output=format_output("Setting fan speed to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: FanSpeedMode):
        """Set fan speed."""
        return self.set_property("fan_speed", fan_speed)

    @command()
    def fan_speed_presets(self) -> Dict[str, int]:
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
