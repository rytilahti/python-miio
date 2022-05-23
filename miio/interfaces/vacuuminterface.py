"""`VacuumInterface` is an interface (abstract class) with shared API for all vacuum
devices."""
from abc import abstractmethod
from typing import Dict

# Dictionary of predefined fan speeds
FanspeedPresets = Dict[str, int]


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
