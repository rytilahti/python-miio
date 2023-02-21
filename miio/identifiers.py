"""Compat layer for homeassistant."""
from enum import Enum, auto


class StandardIdentifier(Enum):
    """Base class for standardized descriptor identifiers."""


class VacuumId(StandardIdentifier):
    """Vacuum-specific standardized descriptor identifiers.

    TODO: this is a temporary solution, and might be named to 'Vacuum' later on.
    """

    # Actions
    Start = "vacuum:start-sweep"
    Stop = "vacuum:stop-sweeping"
    Pause = "vacuum:pause-sweeping"
    ReturnHome = "battery:start-charge"
    Locate = "identify:identify"
    Spot = "vacuum:spot-cleaning"  # TODO: invented name

    # Settings
    FanSpeed = "vacuum:fan-speed"  # TODO: invented name
    FanSpeedPreset = "vacuum:mode"

    # Sensors
    State = "vacuum:status"
    ErrorMessage = "vacuum:fault"
    Battery = "battery:level"


class FanId(StandardIdentifier):
    """Standard identifiers for fans."""

    On = "fan:on"
    Oscillate = "fan:horizontal-swing"
    Angle = "fan:horizontal-angle"
    Speed = "fan:speed-level"
    Preset = "fan:mode"
    Toggle = "fan:toggle"


class LightId(StandardIdentifier):
    """Standard identifiers for lights."""

    On = "light:on"
    Brightness = "light:brightness"
    ColorTemperature = "light:color-temperature"
    Color = "light:color"


class VacuumState(Enum):
    """Vacuum state enum.

    This offers a simplified API to the vacuum state.

    # TODO: the interpretation of simplified state should be done downstream.
    """

    Unknown = auto()
    Cleaning = auto()
    Returning = auto()
    Idle = auto()
    Docked = auto()
    Paused = auto()
    Error = auto()
