"""`VacuumInterface` is an interface (abstract class) with shared API for all vacuum
devices."""
from abc import abstractmethod
from typing import Dict


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
        """Pause cleaning."""
        raise RuntimeError("`pause` not supported")

    @abstractmethod
    def fan_speed_presets(self) -> Dict[str, int]:
        """Return dictionary containing supported fan speeds."""

    @abstractmethod
    def set_fan_speed_preset(self, speed: int) -> None:
        """Sets fan speed preset value.

        :param speed: integer value from fan_speed_presets() method
        """
