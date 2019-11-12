import logging
from collections import defaultdict
from datetime import timedelta
from enum import Enum

import click

from .click_common import command, format_output
from .device import Device
from .utils import pretty_seconds

_LOGGER = logging.getLogger(__name__)


class ViomiVacuumSpeed(Enum):
    Silent = 0
    Standard = 1
    Medium = 2
    Turbo = 3


class ViomiVacuumState(Enum):
    Idle = 1
    Idle2 = 2
    Cleaning = 3
    Returning = 4
    Docked = 5


class ViomiVacuumStatus:
    def __init__(self, data):
        # ["run_state","mode","err_state","battary_life","box_type","mop_type","s_time","s_area",
        # [ 5,          0,     2103,       85,            3,         1,         0,       0,
        # "suction_grade","water_grade","remember_map","has_map","is_mop","has_newmap"]'
        # 1,               11,           1,            1,         1,       0          ]
        self.data = data

    @property
    def state(self):
        return ViomiVacuumState(self.data["run_state"])

    @property
    def is_on(self) -> bool:
        """True if cleaning."""
        return self.state == ViomiVacuumState.Cleaning

    @property
    def mode(self):
        """TODO: unknown values"""
        return self.data["mode"]

    @property
    def error(self):
        """TODO: unknown values"""
        return self.data["error_state"]

    @property
    def battery(self) -> int:
        """Battery in percentage."""
        return self.data["battary_life"]

    @property
    def box_type(self):
        """TODO: unknown values"""
        return self.data["box_type"]

    @property
    def mop_type(self):
        """TODO: unknown values"""
        return self.data["mop_type"]

    @property
    def clean_time(self) -> timedelta:
        return pretty_seconds(self.data["s_time"])

    @property
    def clean_area(self) -> float:
        """TODO: unknown values"""
        return self.data["s_area"]

    @property
    def fanspeed(self):
        return ViomiVacuumSpeed(self.data["suction_grade"])

    @property
    def water_level(self):
        """TODO: unknown values, percentage?"""
        return self.data["water_grade"]

    @property
    def remember_map(self) -> bool:
        return bool(self.data["remember_map"])

    @property
    def has_map(self) -> bool:
        return bool(self.data["has_map"])

    @property
    def has_new_map(self) -> bool:
        return bool(self.data["has_newmap"])

    @property
    def is_mop(self) -> bool:
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
        self.send("set_suction", [ViomiVacuumSpeed(speed.capitalize()).value])

    @command()
    def home(self):
        """Return to home."""
        self.send("set_charge", [1])
