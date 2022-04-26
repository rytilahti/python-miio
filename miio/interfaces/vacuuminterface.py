"""`VacuumInterface` is an interface (abstract class) with shared API for all vacuum
devices."""
from abc import abstractmethod
from typing import Dict

# dictionary of predefined fan speed;  see corresponding method for detailed description
FanspeedPresets = Dict[str, int]


class VacuumInterface:
    """Vacuum API interface."""

    @abstractmethod
    def home(self):
        """Return to home."""

    @abstractmethod
    def start(self):
        """Start cleaning."""

    @abstractmethod
    def stop(self):
        """Validate that Stop cleaning."""

    def pause(self):
        """Pause cleaning.

        :raise RuntimeError: if the method is not supported for the device
        """
        raise RuntimeError("`pause` not supported")

    @abstractmethod
    def fan_speed_presets(self) -> FanspeedPresets:
        """Return dictionary containing supported fan speeds.

        Dictionary where:
        - key is name (identifier)
        - value is integer representation; usable as argument for set_fan_speed_preset() method
        """

    @abstractmethod
    def set_fan_speed_preset(self, speed: int) -> None:
        """Sets fan speed preset value.

        :param speed: integer value from fan_speed_presets() method
        :raise RuntimeError: if argument is not recognized preset speed for the device
        """
