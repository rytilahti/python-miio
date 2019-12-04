import logging
from collections import defaultdict
from datetime import timedelta
from enum import Enum

import click

from .click_common import EnumType, command, format_output
from .device import Device
from .utils import pretty_seconds
from .vacuumcontainers import DNDStatus

_LOGGER = logging.getLogger(__name__)


class ViomiVacuumSpeed(Enum):
    Silent = 0
    Standard = 1
    Medium = 2
    Turbo = 3


class ViomiVacuumState(Enum):
    IdleNotDocked = 0
    Idle = 1
    Idle2 = 2
    Cleaning = 3
    Returning = 4
    Docked = 5


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
        return ViomiVacuumState(self.data["run_state"])

    @property
    def is_on(self) -> bool:
        """True if cleaning."""
        return self.state == ViomiVacuumState.Cleaning

    @property
    def mode(self):
        """Active mode.

        TODO: unknown values
        """
        return self.data["mode"]

    @property
    def error(self):
        """Error code.

        TODO: unknown values
        """
        return self.data["error_state"]

    @property
    def battery(self) -> int:
        """Battery in percentage."""
        return self.data["battary_life"]

    @property
    def box_type(self):
        """Box type.

        TODO: unknown values"""
        return self.data["box_type"]

    @property
    def mop_type(self):
        """Mop type.

        TODO: unknown values"""
        return self.data["mop_type"]

    @property
    def clean_time(self) -> timedelta:
        """Cleaning time."""
        return pretty_seconds(self.data["s_time"])

    @property
    def clean_area(self) -> float:
        """Cleaned area.

        TODO: unknown values
        """
        return self.data["s_area"]

    @property
    def fanspeed(self) -> ViomiVacuumSpeed:
        """Current fan speed."""
        return ViomiVacuumSpeed(self.data["suction_grade"])

    @property
    def water_level(self):
        """Tank's water level.

        TODO: unknown values, percentage?
        """
        return self.data["water_grade"]

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
    def is_mop(self) -> bool:
        """True if mopping."""
        return bool(self.data["is_mop"])


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
            "Box type: {result.box_type}\n"
            "Mop type: {result.mop_type}\n"
            "Clean time: {result.clean_time}\n"
            "Clean area: {result.clean_area}\n"
            "Water level: {result.water_level}\n"
            "Remember map: {result.remember_map}\n"
            "Has map: {result.has_map}\n"
            "Has new map: {result.has_new_map}\n"
            "Is mop: {result.is_mop}\n",
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

        values = self.send("get_prop", properties)

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

    @command(click.argument("speed", type=str))
    def set_fan_speed(self, speed: str):
        """Set fanspeed [silent, standard, medium, turbo]."""
        self.send("set_suction", [ViomiVacuumSpeed(speed.capitalize()).value])

    @command()
    def home(self):
        """Return to home."""
        self.send("set_charge", [1])

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

    @command(click.argument("language", type=EnumType(ViomiLanguage, False)))
    def set_language(self, language: ViomiLanguage):
        """Set the device's audio language."""
        return self.send("set_language", [language.value])

    @command(click.argument("state", type=EnumType(ViomiLedState, False)))
    def led(self, state: ViomiLedState):
        """Switch the button leds on or off."""
        return self.send("set_light", [state.value])

    @command(click.argument("mode", type=EnumType(ViomiCarpetTurbo)))
    def carpet_mode(self, mode: ViomiCarpetTurbo):
        """Set the carpet mode."""
        return self.send("set_carpetturbo", [mode.value])
