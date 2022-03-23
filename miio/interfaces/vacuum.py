from typing import Dict, Protocol, runtime_checkable

from miio import DeviceStatus

FanspeedPresets = Dict[str, int]


@runtime_checkable
class Vacuum(Protocol):
    def start(self):
        """Start vacuuming."""

    def pause(self):
        """Pause vacuuming."""

    def stop(self):
        """Stop vacuuming."""

    def home(self):
        """Return back to base."""

    def find(self):
        """Request vacuum to play a sound to reveal its location."""

    def status(self) -> DeviceStatus:
        """Return device status."""

    def set_fan_speed(self, int):
        """Set fan speed."""

    def fan_speed_presets(self) -> FanspeedPresets:
        """Return available fan speed presets."""
