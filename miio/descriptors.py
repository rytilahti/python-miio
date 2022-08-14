"""This module contains integration descriptors.

These can be used to make specifically interesting pieces of functionality
visible to downstream users.

TBD: Some descriptors are created automatically based on the status container classes,
but developers can override :func:buttons(), :func:sensors(), .. to expose more features.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, Optional

from attrs import define


@dataclass
class ButtonDescriptor:
    """Describes a button exposed by the device."""

    id: str
    name: str
    method_name: str
    method: Optional[Callable] = None
    extras: Optional[Dict] = None


@dataclass
class SensorDescriptor:
    """Describes a sensor exposed by the device.

    This information can be used by library users to programatically
    access information what types of data is available to display to users.

    Prefer :meth:`@sensor <miio.devicestatus.sensor>` for constructing these.
    """

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
    setter_name: Optional[str] = None
    setter: Optional[Callable] = None
    extras: Optional[Dict] = None


@define(kw_only=True)
class SettingDescriptor:
    """Presents a settable value."""

    id: str
    name: str
    property: str
    unit: str
    setter: Optional[Callable] = None
    setter_name: Optional[str] = None


class SettingType(Enum):
    Number = auto()
    Boolean = auto()
    Enum = auto()


@define(kw_only=True)
class EnumSettingDescriptor(SettingDescriptor):
    """Presents a settable, enum-based value."""

    type: SettingType = SettingType.Enum
    choices_attribute: Optional[str] = None
    choices: Optional[Enum] = None
    extras: Optional[Dict] = None


@define(kw_only=True)
class NumberSettingDescriptor(SettingDescriptor):
    """Presents a settable, numerical value."""

    min_value: int
    max_value: int
    step: int
    type: SettingType = SettingType.Number
    extras: Optional[Dict] = None
