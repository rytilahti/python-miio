import logging
from datetime import timedelta
from enum import Enum
from typing import Dict

import click

from miio.click_common import EnumType, command, format_output
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
MIJIA_VACUUM_V1 = "mijia.vacuum.v1"
MIJIA_VACUUM_V2 = "mijia.vacuum.v2"

SUPPORTED_MODELS = [MIJIA_VACUUM_V1, MIJIA_VACUUM_V2]

MAPPING = {
    # https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:vacuum:0000A006:mijia-v1:1
    "battery": {"siid": 3, "piid": 1},
    "charge_state": {"siid": 3, "piid": 2},
    "error_code": {"siid": 2, "piid": 2},
    "state": {"siid": 2, "piid": 1},
    "fan_speed": {"siid": 2, "piid": 6},
    "operating_mode": {"siid": 2, "piid": 4},
    "mop_state": {"siid": 16, "piid": 1},
    "water_level": {"siid": 2, "piid": 5},
    "main_brush_life_level": {"siid": 14, "piid": 1},
    "main_brush_time_left": {"siid": 14, "piid": 2},
    "side_brush_life_level": {"siid": 15, "piid": 1},
    "side_brush_time_left": {"siid": 15, "piid": 2},
    "filter_life_level": {"siid": 11, "piid": 1},
    "filter_time_left": {"siid": 11, "piid": 2},
    "clean_area": {"siid": 9, "piid": 1},
    "clean_time": {"siid": 9, "piid": 2},
    # totals always return 0
    "total_clean_area": {"siid": 9, "piid": 3},
    "total_clean_time": {"siid": 9, "piid": 4},
    "total_clean_count": {"siid": 9, "piid": 5},
    "home": {"siid": 2, "aiid": 3},
    "find": {"siid": 6, "aiid": 1},
    "start": {"siid": 2, "aiid": 1},
    "stop": {"siid": 2, "aiid": 2},
    "reset_main_brush_life_level": {"siid": 14, "aiid": 1},
    "reset_side_brush_life_level": {"siid": 15, "aiid": 1},
    "reset_filter_life_level": {"siid": 11, "aiid": 1},
}

MIOT_MAPPING = {model: MAPPING for model in SUPPORTED_MODELS}

ERROR_CODES = {
    0: "No error",
    1: "Left Wheel stuck",
    2: "Right Wheel stuck",
    3: "Cliff error",
    4: "Low battery",
    5: "Bump error",
    6: "Main Brush Error",
    7: "Side Brush Error",
    8: "Fan Motor Error",
    9: "Dustbin Error",
    10: "Charging Error",
    11: "No Water Error",
    12: "Pick Up Error",
}


class G1ChargeState(Enum):
    """Charging Status."""

    Discharging = 0
    Charging = 1
    FullyCharged = 2


class G1State(Enum):
    """Vacuum Status."""

    Idle = 1
    Sweeping = 2
    Paused = 3
    Error = 4
    Charging = 5
    GoCharging = 6


class G1Consumable(Enum):
    """Consumables."""

    MainBrush = "main_brush_life_level"
    SideBrush = "side_brush_life_level"
    Filter = "filter_life_level"


class G1VacuumMode(Enum):
    """Vacuum Mode."""

    GlobalClean = 1
    SpotClean = 2
    Wiping = 3


class G1WaterLevel(Enum):
    """Water Flow Level."""

    Level1 = 1
    Level2 = 2
    Level3 = 3


class G1FanSpeed(Enum):
    """Fan speeds."""

    Mute = 0
    Standard = 1
    Medium = 2
    High = 3


class G1Languages(Enum):
    """Languages."""

    Chinese = 0
    English = 1


class G1MopState(Enum):
    """Mop Status."""

    Off = 0
    On = 1


class G1Status(DeviceStatus):
    """Container for status reports from Mijia Vacuum G1."""

    def __init__(self, data):
        """Response (MIoT format) of a Mijia Vacuum G1 (mijia.vacuum.v2)

        Example::

            [
                 {'did': 'battery', 'siid': 3, 'piid': 1, 'code': 0, 'value': 100},
                 {'did': 'charge_state', 'siid': 3, 'piid': 2, 'code': 0, 'value': 2},
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
                 {'did': 'filter_life_level', 'siid': 11, 'piid': 1, 'code': 0, 'value': 99},
                 {'did': 'filter_time_left', 'siid': 11, 'piid': 2, 'code': 0, 'value': 8959},
                 {'did': 'clean_area', 'siid': 9, 'piid': 1, 'code': 0, 'value': 0},
                 {'did': 'clean_time', 'siid': 9, 'piid': 2, 'code': 0, 'value': 0}
            ]
        """
        self.data = data

    @property
    def battery(self) -> int:
        """Battery Level."""
        return self.data["battery"]

    @property
    def charge_state(self) -> G1ChargeState:
        """Charging State."""
        return G1ChargeState(self.data["charge_state"])

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
    def state(self) -> G1State:
        """Vacuum Status."""
        return G1State(self.data["state"])

    @property
    def fan_speed(self) -> G1FanSpeed:
        """Fan Speed."""
        return G1FanSpeed(self.data["fan_speed"])

    @property
    def operating_mode(self) -> G1VacuumMode:
        """Operating Mode."""
        return G1VacuumMode(self.data["operating_mode"])

    @property
    def mop_state(self) -> G1MopState:
        """Mop State."""
        return G1MopState(self.data["mop_state"])

    @property
    def water_level(self) -> G1WaterLevel:
        """Water Level."""
        return G1WaterLevel(self.data["water_level"])

    @property
    def main_brush_life_level(self) -> int:
        """Main Brush Life Level in %."""
        return self.data["main_brush_life_level"]

    @property
    def main_brush_time_left(self) -> timedelta:
        """Main Brush Remaining Time in Minutes."""
        return timedelta(minutes=self.data["main_brush_time_left"])

    @property
    def side_brush_life_level(self) -> int:
        """Side Brush Life Level in %."""
        return self.data["side_brush_life_level"]

    @property
    def side_brush_time_left(self) -> timedelta:
        """Side Brush Remaining Time in Minutes."""
        return timedelta(minutes=self.data["side_brush_time_left"])

    @property
    def filter_life_level(self) -> int:
        """Filter Life Level in %."""
        return self.data["filter_life_level"]

    @property
    def filter_time_left(self) -> timedelta:
        """Filter remaining time."""
        return timedelta(minutes=self.data["filter_time_left"])

    @property
    def clean_area(self) -> int:
        """Clean Area in cm2."""
        return self.data["clean_area"]

    @property
    def clean_time(self) -> timedelta:
        """Clean time."""
        return timedelta(minutes=self.data["clean_time"])


class G1CleaningSummary(DeviceStatus):
    """Container for cleaning summary from Mijia Vacuum G1.

    Response (MIoT format) of a Mijia Vacuum G1 (mijia.vacuum.v2)::

        [
            {'did': 'total_clean_area', 'siid': 9, 'piid': 3, 'code': 0, 'value': 0},
            {'did': 'total_clean_time', 'siid': 9, 'piid': 4, 'code': 0, 'value': 0},
            {'did': 'total_clean_count', 'siid': 9, 'piid': 5, 'code': 0, 'value': 0}
        ]
    """

    def __init__(self, data) -> None:
        self.data = data

    @property
    def total_clean_count(self) -> int:
        """Total Number of Cleanings."""
        return self.data["total_clean_count"]

    @property
    def total_clean_area(self) -> int:
        """Total Area Cleaned in m2."""
        return self.data["total_clean_area"]

    @property
    def total_clean_time(self) -> timedelta:
        """Total Cleaning Time."""
        return timedelta(hours=self.data["total_clean_area"])


class G1Vacuum(MiotDevice):
    """Support for G1 vacuum (G1, mijia.vacuum.v2)."""

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
    def status(self) -> G1Status:
        """Retrieve properties."""

        return G1Status(
            {
                # max_properties limited to 10 to avoid "Checksum error"
                # messages from the device.
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping(max_properties=10)
            }
        )

    @command(
        default_output=format_output(
            "",
            "Total Cleaning Count: {result.total_clean_count}\n"
            "Total Cleaning Time: {result.total_clean_time}\n"
            "Total Cleaning Area: {result.total_clean_area}\n",
        )
    )
    def cleaning_summary(self) -> G1CleaningSummary:
        """Retrieve properties."""

        return G1CleaningSummary(
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
    def find(self) -> None:
        """Find the robot."""
        return self.call_action_from_mapping("find")

    @command(click.argument("consumable", type=G1Consumable))
    def consumable_reset(self, consumable: G1Consumable):
        """Reset consumable information.

        CONSUMABLE=main_brush_life_level|side_brush_life_level|filter_life_level
        """
        if consumable.name == G1Consumable.MainBrush:
            return self.call_action_from_mapping("reset_main_brush_life_level")
        elif consumable.name == G1Consumable.SideBrush:
            return self.call_action_from_mapping("reset_side_brush_life_level")
        elif consumable.name == G1Consumable.Filter:
            return self.call_action_from_mapping("reset_filter_life_level")

    @command(
        click.argument("fan_speed", type=EnumType(G1FanSpeed)),
        default_output=format_output("Setting fan speed to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: G1FanSpeed):
        """Set fan speed."""
        return self.set_property("fan_speed", fan_speed.value)

    @command()
    def fan_speed_presets(self) -> Dict[str, int]:
        """Return available fan speed presets."""
        return {x.name: x.value for x in G1FanSpeed}

    @command(click.argument("speed", type=int))
    def set_fan_speed_preset(self, speed_preset: int) -> None:
        """Set fan speed preset speed."""
        if speed_preset not in self.fan_speed_presets().values():
            raise ValueError(
                f"Invalid preset speed {speed_preset}, not in: {self.fan_speed_presets().values()}"
            )
        return self.set_property("fan_speed", speed_preset)
