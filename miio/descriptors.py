"""This module contains descriptors.

The descriptors contain information that can be used to provide generic, dynamic user-interfaces.

If you are a downstream developer, use :func:`~miio.device.Device.sensors()`,
:func:`~miio.device.Device.settings()`, :func:`~miio.device.Device.switches()`, and
:func:`~miio.device.Device.buttons()` to access the functionality exposed by the integration developer.

If you are developing an integration, prefer :func:`~miio.devicestatus.sensor`, :func:`~miio.devicestatus.sensor`, and
:func:`~miio.devicestatus.sensor` decorators over creating the descriptors manually.
If needed, you can override the methods listed to add more descriptors to your integration.
"""
from enum import Enum, auto
from typing import Callable, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class ButtonDescriptor:
    """Describes a button exposed by the device."""

    id: str
    name: str
    method_name: str
    method: Optional[Callable] = None
    extras: Optional[Dict] = None


@attr.s(auto_attribs=True)
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


@attr.s(auto_attribs=True)
class SwitchDescriptor:
    """Presents toggleable switch."""

    id: str
    name: str
    property: str
    setter_name: Optional[str] = None
    setter: Optional[Callable] = None
    extras: Optional[Dict] = None


@attr.s(auto_attribs=True, kw_only=True)
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


@attr.s(auto_attribs=True, kw_only=True)
class EnumSettingDescriptor(SettingDescriptor):
    """Presents a settable, enum-based value."""

    type: SettingType = SettingType.Enum
    choices_attribute: Optional[str] = None
    choices: Optional[Enum] = None
    extras: Optional[Dict] = None


@attr.s(auto_attribs=True, kw_only=True)
class NumberSettingDescriptor(SettingDescriptor):
    """Presents a settable, numerical value."""

    min_value: int
    max_value: int
    step: int
    type: SettingType = SettingType.Number
    extras: Optional[Dict] = None
