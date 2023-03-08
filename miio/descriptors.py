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
        return s


@attr.s(auto_attribs=True)
class Descriptor:
    """Base class for all descriptors."""

    #: Unique identifier.
    id: str
    #: Human readable name.
    name: str
    #: Type of the property, if applicable.
    type: Optional[type] = None
    #: Unit of the property, if applicable.
    unit: Optional[str] = None
    #: Name of the attribute in the status container that contains the value, if applicable.
    status_attribute: Optional[str] = None
    #: Additional data related to this descriptor.
    extras: Dict = attr.ib(factory=dict, repr=False)
    #: Access flags (read, write, execute) for the described item.
    access: AccessFlags = attr.ib(default=AccessFlags(0))

    @property
    def __cli_output__(self) -> str:
        """Return a string presentation for the cli."""
        s = f"{self.name} ({self.id})\n"
        if self.type:
            s += f"\tType: {self.type}\n"
        if self.unit:
            s += f"\tUnit: {self.unit}\n"
        if self.status_attribute:
            s += f"\tAttribute: {self.status_attribute}\n"
        s += f"\tAccess: {self.access}\n"
        if self.extras:
            s += f"\tExtras: {self.extras}\n"

        return s


@attr.s(auto_attribs=True)
class ActionDescriptor(Descriptor):
    """Describes a button exposed by the device."""

    # Callable to execute the action.
    method: Optional[Callable] = attr.ib(default=None, repr=False)
    #: Name of the method in the device class that can be used to execute the action.
    method_name: Optional[str] = attr.ib(default=None, repr=False)
    inputs: Optional[List[Any]] = attr.ib(default=None, repr=True)

    access: AccessFlags = attr.ib(default=AccessFlags.Execute)

    @property
    def __cli_output__(self) -> str:
        """Return a string presentation for the cli."""
        s = super().__cli_output__
        if self.inputs:
            s += f"\tInputs: {self.inputs}\n"

        return s


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
     :meth:`@setting <miio.devicestatus.setting>` for constructing these.
    """

    #: Name of the attribute in the status container that contains the value.
    status_attribute: str
    #: Sensors are read-only and settings are (usually) read-write.
    access: AccessFlags = attr.ib(default=AccessFlags.Read)

    #: Constraint type defining the allowed values for an integer property.
    constraint: PropertyConstraint = attr.ib(default=PropertyConstraint.Unset)
    #: Callable to set the value of the property.
    setter: Optional[Callable] = attr.ib(default=None, repr=False)
    #: Name of the method in the device class that can be used to set the value.
    #: If set, the callable with this name will override the `setter` attribute.
    setter_name: Optional[str] = attr.ib(default=None, repr=False)

    @property
    def __cli_output__(self) -> str:
        """Return a string presentation for the cli."""
        s = super().__cli_output__

        if self.setter:
            s += f"\tSetter: {self.setter}\n"
        if self.setter_name:
            s += f"\tSetter Name: {self.setter_name}\n"
        if self.constraint:
            s += f"\tConstraint: {self.constraint}\n"

        return s


@attr.s(auto_attribs=True, kw_only=True)
class EnumDescriptor(PropertyDescriptor):
    """Presents a settable, enum-based value."""

    constraint: PropertyConstraint = PropertyConstraint.Choice
    #: Name of the attribute in the device class that returns the choices.
    choices_attribute: Optional[str] = attr.ib(default=None, repr=False)
    #: Enum class containing the available choices.
    choices: Optional[Type[Enum]] = attr.ib(default=None, repr=False)

    @property
    def __cli_output__(self) -> str:
        """Return a string presentation for the cli."""
        s = super().__cli_output__
        if self.choices:
            s += f"\tChoices: {self.choices}\n"

        return s


@attr.s(auto_attribs=True, kw_only=True)
class RangeDescriptor(PropertyDescriptor):
    """Presents a settable, numerical value constrained by min, max, and step.

    If `range_attribute` is set, the named property that should return a
    :class:`ValidSettingRange` object to override the {min,max}_value and step values.
    """

    #: Minimum value for the property.
    min_value: int
    #: Maximum value for the property.
    max_value: int
    #: Step size for the property.
    step: int
    #: Name of the attribute in the device class that returns the range.
    #: If set, this will override the individual min/max/step values.
    range_attribute: Optional[str] = attr.ib(default=None)
    type: type = int
    constraint: PropertyConstraint = PropertyConstraint.Range

    @property
    def __cli_output__(self) -> str:
        """Return a string presentation for the cli."""
        s = super().__cli_output__
        s += f"\tRange: {self.min_value} - {self.max_value} (step {self.step})\n"
        return s
