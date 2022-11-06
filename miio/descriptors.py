"""This module contains descriptors.

The descriptors contain information that can be used to provide generic, dynamic user-interfaces.

If you are a downstream developer, use :func:`~miio.device.Device.sensors()`,
:func:`~miio.device.Device.settings()`, and
:func:`~miio.device.Device.actions()` to access the functionality exposed by the integration developer.

If you are developing an integration, prefer :func:`~miio.devicestatus.sensor`, :func:`~miio.devicestatus.setting`, and
:func:`~miio.devicestatus.action` decorators over creating the descriptors manually.
If needed, you can override the methods listed to add more descriptors to your integration.
"""
from enum import Enum, auto
from typing import Callable, Dict, Optional, Type

import attr


@attr.s(auto_attribs=True)
class ActionDescriptor:
    """Describes a button exposed by the device."""

    id: str
    name: str
    method_name: Optional[str] = None
    method: Optional[Callable] = None
    extras: Dict = attr.ib(factory=dict)


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
    extras: Dict = attr.ib(factory=dict)


class SettingType(Enum):
    Undefined = auto()
    Number = auto()
    Boolean = auto()
    Enum = auto()


@attr.s(auto_attribs=True, kw_only=True)
class SettingDescriptor:
    """Presents a settable value."""

    id: str
    name: str
    property: str
    unit: Optional[str] = None
    type = SettingType.Undefined
    setter: Optional[Callable] = None
    setter_name: Optional[str] = None
    extras: Dict = attr.ib(factory=dict)

    def cast_value(self, value):
        """Casts value to the expected type."""
        cast_map = {
            SettingType.Boolean: bool,
            SettingType.Enum: int,
            SettingType.Number: int,
        }
        return cast_map[self.type](int(value))


@attr.s(auto_attribs=True, kw_only=True)
class BooleanSettingDescriptor(SettingDescriptor):
    """Presents a settable boolean value."""

    type: SettingType = SettingType.Boolean


@attr.s(auto_attribs=True, kw_only=True)
class EnumSettingDescriptor(SettingDescriptor):
    """Presents a settable, enum-based value."""

    type: SettingType = SettingType.Enum
    choices_attribute: Optional[str] = None
    choices: Optional[Type[Enum]] = None


@attr.s(auto_attribs=True, kw_only=True)
class NumberSettingDescriptor(SettingDescriptor):
    """Presents a settable, numerical value."""

    min_value: int
    max_value: int
    step: int
    type: SettingType = SettingType.Number
