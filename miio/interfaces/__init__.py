"""Interfaces API."""

from .lightinterface import ColorTemperatureRange, LightInterface
from .vacuuminterface import FanspeedPresets, VacuumInterface

__all__ = [
    "FanspeedPresets",
    "VacuumInterface",
    "LightInterface",
    "ColorTemperatureRange",
]
