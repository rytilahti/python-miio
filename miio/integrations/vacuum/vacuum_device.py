"""`VacuumDevice` is abstract class with shared API for all vacuum devices
`VacuumMiotDevice` is abstract class with shared API for all vacuum MIOT devices."""
from abc import abstractmethod

from miio.device import Device
from miio.miot_device import MiotDevice


class VacuumDevice(Device):
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


class VacuumMiotDevice(VacuumDevice, MiotDevice):
    """Vacuum API Interface for Miot devices."""

    @abstractmethod
    def start(self):
        """Start cleaning."""
