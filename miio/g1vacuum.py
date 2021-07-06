import logging
from typing import Any, Dict
from datetime import timedelta
from enum import Enum
import click
from .click_common import EnumType, command, format_output
from .miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)
MIJIA_VACUUM_V2 = "mijia.vacuum.v2"

MIOT_MAPPING = {
    MIJIA_VACUUM_V2: {
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
    #  "main_brush_life_time": {"siid": 14, "piid": 2},
    "side_brush_life_level": {"siid": 15, "piid": 1},
    #  "side_brush_life_time": {"siid": 15, "piid": 2},
    "filter_life_level": {"siid": 11, "piid": 1},
    #  "filter_life_time": {"siid": 11, "piid": 2},
    "clean_area": {"siid": 9, "piid": 1},
    "clean_time": {"siid": 18, "piid": 5},
    "total_clean_count": {"siid": 9, "piid": 5},
    #   "total_clean_area": {"siid": 9, "piid": 3}, #throws error
    #  "dnd_enabled": {"siid": 12, "piid": 2},
    #  "audio_volume": {"siid": 4, "piid": 2},
    #  "direction_key": {"siid": 8, "piid": 1}
    "home": {"siid": 2, "aiid": 3},
    "find": {"siid": 6, "aiid": 1},
    "start": {"siid": 2, "aiid": 1},
    "stop": {"siid": 2, "aiid": 2},
    "reset_main_brush_life_level":  {"siid": 14, "aiid": 1},
    "reset_side_brush_life_level":  {"siid": 15, "aiid": 1},
    "reset_filter_life_level":  {"siid": 11, "aiid": 1}
    }
}

error_codes = {
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
    12: "Pick Up Error"
}

class G1ChargeState(Enum):
    Discharging = 0
    Charging = 1
    FullyCharged = 2

class G1State(Enum):
    """Vacuum Status"""
    Idle = 1
    Sweeping = 2
    Paused = 3
    Error = 4
    Charging = 5
    GoCharging = 6

class G1Consumable(Enum):
    """Consumables"""
    MainBrush = "main_brush_life_level"
    SideBrush = "side_brush_life_level"
    Filter = "filter_life_level"

class G1VacuumMode(Enum):
    """Vacuum Mode"""
    GlobalClean = 1
    SpotClean = 2
    Wiping = 3

class G1WaterLevel(Enum):
    """Water Flow Level"""
    Level1 = 1
    Level2 = 2
    Level3 = 3

class G1FanSpeed(Enum):
    """Fan speeds, same as for ViomiVacuum."""
    Mute = 0
    Standard = 1
    Medium = 2
    High = 3

class G1Languages(Enum):
    Chinese = 0
    English = 1

class G1MopState(Enum):
    Off = 0
    On = 1


class G1Status(DeviceStatus):
    """Container for status reports from the Mijia Vacuum G1."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def battery(self) -> int:
        """Battery Level."""
        return self.data["battery"]

    @property
    def charge_state(self) -> G1ChargeState:
        """Charging State."""
        return G1ChargeState[G1ChargeState(self.data["charge_state"]).name]

    @property
    def error_code(self) -> int:
        """Error code as returned by the device."""
        return int(self.data["error_code"])

    @property
    def error(self) -> str:
        """Human readable error description, see also :func:`error_code`."""
        try:
            return error_codes[self.error_code]
        except KeyError:
            return "Definition missing for error %s" % self.error_code

    @property
    def state(self) -> G1State:
        """Vacuum Status."""
        return G1State[G1State(self.data["state"]).name]

    @property
    def fan_speed(self) -> G1FanSpeed:
        """Fan Speed."""
        return G1FanSpeed[G1FanSpeed(self.data["fan_speed"]).name]

    @property
    def operating_mode(self) -> G1VacuumMode:
        """Operating Mode."""
        return G1VacuumMode[G1VacuumMode(self.data["operating_mode"]).name]

    @property
    def mop_state(self) -> G1MopState:
        """Mop State."""
        return G1MopState[G1MopState(self.data["mop_state"]).name]

    @property
    def water_level(self) -> G1WaterLevel:
        """Mop State."""
        return G1WaterLevel[G1WaterLevel(self.data["water_level"]).name]

    @property
    def main_brush_life_level(self) -> int:
        """Main Brush Life Level in %."""
        return self.data["main_brush_life_level"]

    @property
    def side_brush_life_level(self) -> int:
        """Side Brush Life Level in %."""
        return self.data["side_brush_life_level"]

    @property
    def filter_life_level(self) -> int:
        """Filter Life Level in %."""
        return self.data["filter_life_level"]

    @property
    def clean_area(self) -> int:
        """Clean Area in cm2."""
        return self.data["clean_area"]

    @property
    def clean_time(self) -> timedelta:
        """Clean Time in Minutes."""
        return self.data["clean_time"]

    @property
    def total_clean_count(self) -> int:
        """Total Clean Count."""
        return self.data["total_clean_count"]




class G1Vacuum(MiotDevice):
    """Support for G1 vacuum (G1, mijia.vacuum.v2)."""

    mapping = MIOT_MAPPING[MIJIA_VACUUM_V2]

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MIJIA_VACUUM_V2,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)
        self.model = model

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
            "Filter Life Level: {result.filter_life_level}%\n"
            "Main Brush Life Level: {result.main_brush_life_level}%\n"
            "Side Brush Life Level: {result.side_brush_life_level}%\n"
            "Clean Area: {result.clean_area}\n"
            "Clean Time: {result.clean_time}\n"
            "Total Clean Count: {result.total_clean_count}\n",
        )
    )

    def status(self) -> G1Status:
        """Retrieve properties."""

        return G1Status(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )


    @command()
    def home(self):
        """Home."""
        return self.call_action("home")

    @command()
    def start(self) -> None:
        """Start Cleaning"""
        return self.call_action("start")

    @command()
    def stop(self):
        """Stop Cleaning"""
        return self.call_action("stop")

    @command()
    def find(self) -> None:
        """Find the robot."""
        return self.call_action("find")

    @command(click.argument("consumable", type=G1Consumable))
    def consumable_reset(self, consumable: G1Consumable):
        """Reset consumable information. CONSUMABLE=main_brush_life_level|side_brush_life_level|filter_life_level"""
        if consumable.name == "MainBrush":
           return self.call_action("reset_main_brush_life_level")
        elif consumable.name == "SideBrush":
           return self.call_action("reset_side_brush_life_level")
        elif consumable.name == "Filter":
           return self.call_action("reset_filter_life_level")

    @command(
        click.argument("fan_speed", type=EnumType(G1FanSpeed)),
        default_output=format_output("Setting fan speed to {fan_speed}"),
    )
    def set_fan_speed(self, fan_speed: G1FanSpeed):
        """Set fan speed."""
        return self.set_property("fan_speed", fan_speed.value)