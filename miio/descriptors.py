"""This module contains integration descriptors.

These can be used to make specifically interesting pieces of functionality
visible to downstream users.

TBD: Some descriptors are created automatically based on the status container classes,
but developers can override :func:buttons(), :func:sensors(), .. to expose more features.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Optional


@dataclass
class ButtonDescriptor:
    id: str
    name: str
    method: Callable
    extras: Optional[Dict] = None


@dataclass
class SensorDescriptor:
    id: str
    type: str
    name: str
    property: str
    unit: Optional[str] = None
    extras: Optional[Dict] = None


@dataclass
class SwitchDescriptor:
    """Presents toggleable switch."""

    id: str
    name: str
    property: str
    setter: Callable


@dataclass
class SettingDescriptor:
    """Presents a settable value."""

    id: str
    name: str
    property: str
    setter: Callable
    unit: str


class SettingType(Enum):
    Number = auto()
    Boolean = auto()
    Enum = auto()


@dataclass
class EnumSettingDescriptor(SettingDescriptor):
    """Presents a settable, enum-based value."""

    choices: List
    type: SettingType = SettingType.Enum
    extras: Optional[Dict] = None


@dataclass
class NumberSettingDescriptor(SettingDescriptor):
    """Presents a settable, numerical value."""

    min_value: int
    max_value: int
    step: int
    type: SettingType = SettingType.Number
    extras: Optional[Dict] = None
