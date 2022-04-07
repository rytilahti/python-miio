"""`VacuumInterface` is an interface (abstract class) with shared API for all vacuum
devices."""
from abc import abstractmethod

from miio import Device


class VacuumInterface(Device):
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
