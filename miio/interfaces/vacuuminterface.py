"""`VacuumInterface` is an interface (abstract class) with shared API for all vacuum
devices."""
from abc import abstractmethod
from enum import Enum, auto
from typing import Dict, Optional

from miio import DeviceStatus

# Dictionary of predefined fan speeds
FanspeedPresets = Dict[str, int]


class VacuumState(Enum):
    """Vacuum state enum.

    This offers a simplified API to the vacuum state.
    """

    Unknown = auto()
    Cleaning = auto()
    Returning = auto()
    Idle = auto()
    Docked = auto()
    Paused = auto()
    Error = auto()


class VacuumDeviceStatus(DeviceStatus):
    """Status container for vacuums."""

    @abstractmethod
    def vacuum_state(self) -> VacuumState:
        """Return vacuum state."""

    @abstractmethod
    def error(self) -> Optional[str]:
        """Return error message, if errored."""

    @abstractmethod
    def battery(self) -> Optional[int]:
        """Return current battery charge, if available."""


class VacuumInterface:
    """Vacuum API interface."""

    @abstractmethod
    def home(self):
        """Return vacuum robot to home station/dock."""

    @abstractmethod
    def start(self):
        """Start cleaning."""

    @abstractmethod
    def stop(self):
        """Stop cleaning."""

    def pause(self):
        """Pause cleaning.

        :raises RuntimeError: if the method is not supported by the device
        """
        raise RuntimeError("`pause` not supported")

    @abstractmethod
    def fan_speed_presets(self) -> FanspeedPresets:
        """Return available fan speed presets.

        The returned object is a dictionary where the key is user-readable name and the
        value is input for :func:`set_fan_speed_preset()`.
        """

    @abstractmethod
    def set_fan_speed_preset(self, speed_preset: int) -> None:
        """Set fan speed preset speed.

        :param speed_preset: a value from :func:`fan_speed_presets()`
        :raises ValueError: for invalid preset value
        """
