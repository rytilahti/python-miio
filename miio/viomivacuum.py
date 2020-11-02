import logging
import time
from collections import defaultdict
from datetime import timedelta
from enum import Enum
from typing import Dict, List, Optional

import click

from .click_common import EnumType, command, format_output
from .device import Device
from .utils import pretty_seconds
from .vacuumcontainers import ConsumableStatus, DNDStatus

_LOGGER = logging.getLogger(__name__)


ERROR_CODES = {
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


class ViomiConsumableStatus(ConsumableStatus):
    def __init__(self, data: List[int]) -> None:
        # [17, 17, 17, 17]
        self.data = [d * 60 * 60 for d in data]
        self.side_brush_total = timedelta(hours=180)
        self.main_brush_total = timedelta(hours=360)
        self.filter_total = timedelta(hours=180)
        self.mop_total = timedelta(hours=180)

    @property
    def main_brush(self) -> timedelta:
        """Main brush usage time."""
        return pretty_seconds(self.data[0])

    @property
    def main_brush_left(self) -> timedelta:
        """How long until the main brush should be changed."""
        return self.main_brush_total - self.main_brush

    @property
    def side_brush(self) -> timedelta:
        """Side brush usage time."""
        return pretty_seconds(self.data[1])

    @property
    def side_brush_left(self) -> timedelta:
        """How long until the side brush should be changed."""
        return self.side_brush_total - self.side_brush

    @property
    def filter(self) -> timedelta:
        """Filter usage time."""
        return pretty_seconds(self.data[2])

    @property
    def filter_left(self) -> timedelta:
        """How long until the filter should be changed."""
        return self.filter_total - self.filter

    @property
    def mop(self) -> timedelta:
        """Return ``sensor_dirty_time``"""
        return pretty_seconds(self.data[3])

    @property
    def mop_left(self) -> timedelta:
        return self.sensor_dirty_total - self.sensor_dirty

    def __repr__(self) -> str:
        return (
            "<ConsumableStatus main: %s, side: %s, filter: %s, mop: %s>"
            % (  # noqa: E501
                self.main_brush,
                self.side_brush,
                self.filter,
                self.mop,
            )
        )


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


class ViomiMopMode(Enum):
    """Mopping pattern."""

    S = 0
    Y = 1


class ViomiVacuumStatus:
    def __init__(self, data):
        # ["run_state","mode","err_state","battary_life","box_type","mop_type","s_time","s_area",
        # [ 5,          0,     2103,       85,            3,         1,         0,       0,
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
    def is_on(self) -> bool:
        """True if cleaning."""
        cleaning_states = [
            ViomiVacuumState.Cleaning,
            ViomiVacuumState.VacuumingAndMopping,
        ]
        return self.state in cleaning_states

    @property
    def mode(self):
        """Active mode.

        TODO: is this same as mop_type property?
        """
        return ViomiMode(self.data["mode"])

    @property
    def mop_type(self):
        """Unknown mop_type values."""
        return self.data["mop_type"]

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
        return pretty_seconds(self.data["s_time"])

    @property
    def clean_area(self) -> float:
        """Cleaned area in square meters."""
        return self.data["s_area"]

    @property
    def fanspeed(self) -> ViomiVacuumSpeed:
        """Current fan speed."""
        return ViomiVacuumSpeed(self.data["suction_grade"])

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
        """TODO: unknown"""
        return bool(self.data["has_newmap"])

    @property
    def mop_mode(self) -> ViomiMode:
        """Whether mopping is enabled and if so which mode

        TODO: is this really the same as mode?
        """
        return ViomiMode(self.data["is_mop"])


class ViomiVacuum(Device):
    """Interface for Viomi vacuums (viomi.vacuum.v7)."""

    @command(
        default_output=format_output(
            "",
            "State: {result.state}\n"
            "Mode: {result.mode}\n"
            "Error: {result.error}\n"
            "Battery: {result.battery}\n"
            "Fan speed: {result.fanspeed}\n"
            "Box type: {result.bin_type}\n"
            "Mop type: {result.mop_type}\n"
            "Clean time: {result.clean_time}\n"
            "Clean area: {result.clean_area}\n"
            "Water grade: {result.water_grade}\n"
            "Remember map: {result.remember_map}\n"
            "Has map: {result.has_map}\n"
            "Has new map: {result.has_new_map}\n"
            "Mop mode: {result.mop_mode}\n",
        )
    )
    def status(self) -> ViomiVacuumStatus:
        """Retrieve properties."""
        properties = [
            "run_state",
            "mode",
            "err_state",
            "battary_life",
            "box_type",
            "mop_type",
            "s_time",
            "s_area",
            "suction_grade",
            "water_grade",
            "remember_map",
            "has_map",
            "is_mop",
            "has_newmap",
        ]

        values = self.get_properties(properties)

        return ViomiVacuumStatus(defaultdict(lambda: None, zip(properties, values)))

    @command()
    def start(self):
        """Start cleaning."""
        # TODO figure out the parameters
        self.send("set_mode_withroom", [0, 1, 0])

    @command()
    def stop(self):
        """Stop cleaning."""
        self.send("set_mode", [0])

    @command()
    def pause(self):
        """Pause cleaning."""
        self.send("set_mode_withroom", [0, 2, 0])

    @command(click.argument("speed", type=EnumType(ViomiVacuumSpeed)))
    def set_fan_speed(self, speed: ViomiVacuumSpeed):
        """Set fanspeed [silent, standard, medium, turbo]."""
        self.send("set_suction", [speed.value])

    @command(click.argument("watergrade"))
    def set_water_grade(self, watergrade: ViomiWaterGrade):
        """Set water grade [low, medium, high]."""
        self.send("set_suction", [watergrade.value])

    @command()
    def home(self):
        """Return to home."""
        self.send("set_charge", [1])

    @command(
        click.argument("direction", type=EnumType(ViomiMovementDirection)),
        click.option(
            "--duration",
            type=float,
            default=0.5,
            help="number of seconds to perform this movement",
        ),
    )
    def move(self, direction, duration=0.5):
        """Manual movement."""
        start = time.time()
        while time.time() - start < duration:
            self.send("set_direction", [direction.value])
            time.sleep(0.1)
        self.send("set_direction", [ViomiMovementDirection.Stop.value])

    @command(click.argument("mode", type=EnumType(ViomiMode)))
    def clean_mode(self, mode):
        """Set the cleaning mode."""
        self.send("set_mop", [mode.value])

    @command(click.argument("mop_mode", type=EnumType(ViomiMopMode)))
    def mop_mode(self, mop_mode):
        self.send("set_moproute", [mop_mode.value])

    @command()
    def consumable_status(self) -> ViomiConsumableStatus:
        """Return information about consumables."""
        return ViomiConsumableStatus(self.send("get_consumables"))

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
        :param int end_min: End minute"""
        return self.send(
            "set_notdisturb",
            [0 if disable else 1, start_hr, start_min, end_hr, end_min],
        )

    @command(click.argument("language", type=EnumType(ViomiLanguage)))
    def set_language(self, language: ViomiLanguage):
        """Set the device's audio language."""
        return self.send("set_language", [language.value])

    @command(click.argument("state", type=EnumType(ViomiLedState)))
    def led(self, state: ViomiLedState):
        """Switch the button leds on or off."""
        return self.send("set_light", [state.value])

    @command(click.argument("mode", type=EnumType(ViomiCarpetTurbo)))
    def carpet_mode(self, mode: ViomiCarpetTurbo):
        """Set the carpet mode."""
        return self.send("set_carpetturbo", [mode.value])

    @command()
    def fan_speed_presets(self) -> Dict[str, int]:
        """Return dictionary containing supported fanspeeds."""
        return {x.name: x.value for x in list(ViomiVacuumSpeed)}
