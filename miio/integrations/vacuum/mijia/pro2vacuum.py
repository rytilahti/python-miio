import logging
from typing import Dict

import click
from Enum import Enum

from miio.click_common import EnumType, command, format_output
from miio.interfaces import FanspeedPresets, VacuumInterface
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
MI_ROBOT_VACUUM_MOP_PRO_2 = "ijai.vacuum.v3"

SUPPORTED_MODELS = [MI_ROBOT_VACUUM_MOP_PRO_2]

MAPPING = {
    # https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:vacuum:0000A006:ijai-v3:1
    "battery": {"siid": 3, "piid": 1},
    "error_code": {"siid": 2, "piid": 2},
    "state": {"siid": 2, "piid": 1},
    "fan_speed": {"siid": 7, "piid": 5},
    "operating_mode": {"siid": 2, "piid": 4},
    "mop_state": {"siid": 7, "piid": 4},
    "water_level": {"siid": 7, "piid": 6},
    "main_brush_life_level": {"siid": 7, "piid": 10},
    "main_brush_time_left": {"siid": 7, "piid": 11},
    "side_brush_life_level": {"siid": 7, "piid": 8},
    "side_brush_time_left": {"siid": 7, "piid": 9},
    "clean_area": {"siid": 7, "piid": 23},
    "clean_time": {"siid": 7, "piid": 22},
    "home": {"siid": 3, "aiid": 1},
    "start": {"siid": 2, "aiid": 1},
    "stop": {"siid": 2, "aiid": 2},
}

ERROR_CODES: Dict[int, str] = {}

MIOT_MAPPING = {MI_ROBOT_VACUUM_MOP_PRO_2: MAPPING}


class FormattableEnum(Enum):
    def __str__(self):
        return f"{self.name}"


def _enum_as_dict(cls):
    return {x.name: x.value for x in list(cls)}


class DeviceState(FormattableEnum):
    Sleep = 0
    Idle = 1
    Paused = 2
    GoCharging = 3
    Charging = 4
    Sweeping = 5
    SweepingAndMopping = 6
    Mopping = 7
    Upgrading = 8


class SweepMode(FormattableEnum):
    Sweep = 0
    SweepAndMop = 1
    Mop = 2


class SweepType(FormattableEnum):
    Global = 0
    Mop = 1
    Edge = 2
    Area = 3
    Point = 4
    Remote = 5
    Explore = 6
    Room = 7
    Floor = 8


class RepeatState(FormattableEnum):
    Off = 0
    On = 1


class DoorState(FormattableEnum):
    Off = 0
    DustBox = 1
    WaterVolume = 2
    TwoInOneWaterVolume = 3


class ClothState(FormattableEnum):
    Off = 0
    On = 1


class SuctionState(FormattableEnum):
    Off = 0
    EnergySaving = 1
    Standard = 2
    Turbo = 3


class WaterState(FormattableEnum):
    LowLevel = 0
    MediumLevel = 1
    HighLevel = 2


class MopRoute(FormattableEnum):
    BowStyle = 0
    YStyle = 1


class Pro2Status(DeviceStatus):
    """Container for status reports from Mi Robot Vacuum-Mop 2 Pro."""

    def __init__(self, data):
        """Response (MIoT format) of a Mi Robot Vacuum-Mop 2 Pro (ijai.vacuum.v3)

        [
            {'did': 'battery', 'siid': 3, 'piid': 1, 'code': 0, 'value': 100},
            {'did': 'error_code', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'state', 'siid': 2, 'piid': 1, 'code': 0, 'value': 5},
            {'did': 'fan_speed', 'siid': 2, 'piid': 6, 'code': 0, 'value': 1},
            {'did': 'operating_mode', 'siid': 2, 'piid': 4, 'code': 0, 'value': 1},
            {'did': 'mop_state', 'siid': 16, 'piid': 1, 'code': 0, 'value': 0},
            {'did': 'water_level', 'siid': 2, 'piid': 5, 'code': 0, 'value': 2},
            {'did': 'main_brush_life_level', 'siid': 14, 'piid': 1, 'code': 0, 'value': 99},
            {'did': 'main_brush_time_left', 'siid': 14, 'piid': 2, 'code': 0, 'value': 17959}
            {'did': 'side_brush_life_level', 'siid': 15, 'piid': 1, 'code': 0, 'value': 0 },
            {'did': 'side_brush_time_left', 'siid': 15, 'piid': 2', 'code': 0, 'value': 0},
            {'did': 'clean_area', 'siid': 9, 'piid': 1, 'code': 0, 'value': 0},
            {'did': 'clean_time', 'siid': 9, 'piid': 2, 'code': 0, 'value': 0}
            ]"""
        self.data = data

    @property
    def battery(self) -> int:
        """Battery Level."""
        return self.data["battery"]

    @property
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    def error(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        try:
            return ERROR_CODES[self.error_code]
        except KeyError:
            return "Definition missing for error %s" % self.error_code

    @property
    def state(self) -> DeviceState:
        """Vacuum Status."""
        return DeviceState(self.data["state"])

    @property
    def fan_speed(self) -> SuctionState:
        """Fan Speed."""
        return SuctionState(self.data["fan_speed"])

    @property
    def operating_mode(self) -> SweepType:
        """Operating Mode."""
        return SweepType(self.data["operating_mode"])

    @property
    def mop_state(self) -> ClothState:
        """Mop State."""
        return ClothState(self.data["mop_state"])

    @property
    def water_level(self) -> WaterState:
        """Water Level."""
        return WaterState(self.data["water_level"])


class Pro2Vacuum(MiotDevice, VacuumInterface):
    """Support for Mi Robot Vacuum-Mop 2 Pro (ijai.vacuum.v3)."""

    _mappings = MIOT_MAPPING

    @command(
        default_output=format_output(
            "",
            "State: {result.state}\n"
            "Error: {result.error}\n"
            "Battery: {result.battery}%\n"
            "Mode: {result.operating_mode}\n"
            "Mop State: {result.mop_state}\n"
            "Charge Status: {result.charge_state}\n"
            "Fan speed: {result.fan_speed}\n"
            "Water level: {result.water_level}\n"
            "Main Brush Life Level: {result.main_brush_life_level}%\n"
            "Main Brush Life Time: {result.main_brush_time_left}\n"
            "Side Brush Life Level: {result.side_brush_life_level}%\n"
            "Side Brush Life Time: {result.side_brush_time_left}\n"
            "Filter Life Level: {result.filter_life_level}%\n"
            "Filter Life Time: {result.filter_time_left}\n"
            "Clean Area: {result.clean_area}\n"
            "Clean Time: {result.clean_time}\n",
        )
    )
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
        """Home."""
        return self.call_action("home")

    @command()
    def start(self) -> None:
        """Start Cleaning."""
        return self.call_action("start")

    @command()
    def stop(self):
        """Stop Cleaning."""
        return self.call_action("stop")

    @command()
    def find(self) -> None:
        """Find the robot."""
        return self.call_action("find")

    @command(
        click.argument("fan_speed", type=EnumType(SuctionState)),
        default_output=format_output("Setting fan speed to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: SuctionState):
        """Set fan speed."""
        return self.set_property("fan_speed", fan_speed.value)

    @command()
    def fan_speed_presets(self) -> FanspeedPresets:
        """Return available fan speed presets."""
        return _enum_as_dict(SuctionState)

    @command(click.argument("speed", type=int))
    def set_fan_speed_preset(self, speed_preset: int) -> None:
        """Set fan speed preset speed."""
        if speed_preset not in self.fan_speed_presets().values():
            raise ValueError(
                f"Invalid preset speed {speed_preset}, not in: {self.fan_speed_presets().values()}"
            )
        return self.set_property("fan_speed", speed_preset)
