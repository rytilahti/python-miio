"""This module contains descriptors.

The descriptors contain information that can be used to provide generic, dynamic user-interfaces.

If you are a downstream developer, use :func:`~miio.device.Device.properties()`,
:func:`~miio.device.Device.actions()` to access the functionality exposed by the integration developer.

If you are developing an integration, prefer :func:`~miio.devicestatus.sensor`, :func:`~miio.devicestatus.setting`, and
:func:`~miio.devicestatus.action` decorators over creating the descriptors manually.
"""
from enum import Enum, Flag, auto
from typing import Any, Callable, Dict, List, Optional, Type

import attr


@attr.s(auto_attribs=True)
class ValidSettingRange:
    """Describes a valid input range for a property."""

    min_value: int
    max_value: int
    step: int = 1


class AccessFlags(Flag):
    """Defines the access rights for the property behind the descriptor."""

    Read = auto()
    Write = auto()
    Execute = auto()

    def __str__(self):
        """Return pretty printable string representation."""
        s = ""
        s += "r" if self & AccessFlags.Read else "-"
        s += "w" if self & AccessFlags.Write else "-"
        s += "x" if self & AccessFlags.Execute else "-"
        s += ""
        return s


@attr.s(auto_attribs=True)
class Descriptor:
    """Base class for all descriptors."""

    id: str
    name: str
    type: Optional[type] = None
    property: Optional[str] = None
    extras: Dict = attr.ib(factory=dict, repr=False)
    access: AccessFlags = attr.ib(default=AccessFlags.Read | AccessFlags.Write)


@attr.s(auto_attribs=True)
class ActionDescriptor(Descriptor):
    """Describes a button exposed by the device."""

    method_name: Optional[str] = attr.ib(default=None, repr=False)
    method: Optional[Callable] = attr.ib(default=None, repr=False)
    inputs: Optional[List[Any]] = attr.ib(default=None, repr=True)

    access: AccessFlags = attr.ib(default=AccessFlags.Execute)


class PropertyConstraint(Enum):
    """Defines constraints for integer based properties."""

    Unset = auto()
    Range = auto()
    Choice = auto()


@attr.s(auto_attribs=True, kw_only=True)
class PropertyDescriptor(Descriptor):
    """Describes a property exposed by the device.

    This information can be used by library users to programmatically
    access information what types of data is available to display to users.

    Prefer :meth:`@sensor <miio.devicestatus.sensor>` or
     :meth:`@setting <miio.devicestatus.setting>`for constructing these.
    """

    #: The name of the property to use to access the value from a status container.
    property: str
    #: Sensors are read-only and settings are (usually) read-write.
    access: AccessFlags = attr.ib(default=AccessFlags.Read)
    unit: Optional[str] = None

    #: Constraint type defining the allowed values for an integer property.
    constraint: PropertyConstraint = attr.ib(default=PropertyConstraint.Unset)
    #: Callable to set the value of the property.
    setter: Optional[Callable] = attr.ib(default=None, repr=False)
    #: Name of the method in the device class that can be used to set the value.
    #: This will be used to bind the setter callable.
    setter_name: Optional[str] = attr.ib(default=None, repr=False)


@attr.s(auto_attribs=True, kw_only=True)
class EnumDescriptor(PropertyDescriptor):
    """Presents a settable, enum-based value."""

    constraint: PropertyConstraint = PropertyConstraint.Choice
    choices_attribute: Optional[str] = attr.ib(default=None, repr=False)
    choices: Optional[Type[Enum]] = attr.ib(default=None, repr=False)


@attr.s(auto_attribs=True, kw_only=True)
class RangeDescriptor(PropertyDescriptor):
    """Presents a settable, numerical value constrained by min, max, and step.

    If `range_attribute` is set, the named property that should return
    :class:ValidSettingRange will be used to obtain {min,max}_value and step.
    """

    min_value: int
    max_value: int
    step: int
    range_attribute: Optional[str] = attr.ib(default=None)
    type: type = int
    constraint: PropertyConstraint = PropertyConstraint.Range
