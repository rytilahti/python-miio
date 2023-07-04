import logging
from collections import UserDict
from inspect import getmembers
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from .descriptors import (
    AccessFlags,
    ActionDescriptor,
    Descriptor,
    EnumDescriptor,
    PropertyConstraint,
    PropertyDescriptor,
    RangeDescriptor,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from miio import Device


T = TypeVar("T")


class DescriptorCollection(UserDict, Generic[T]):
    """A container of descriptors."""

    def __init__(self, *args, device: "Device"):
        self._device = device
        super().__init__(*args)

    def descriptors_from_object(self, obj):
        """Add descriptors from an object.

        This collects descriptors from the given object and adds them into the collection by:
        1. Checking for '_descriptors' for descriptors created by the class itself.
        2. Going through all members and looking if they have a '_descriptor' attribute set by a decorator
        """
        _LOGGER.debug("Adding descriptors from %s", obj)
        # 1. Check for existence of _descriptors as DeviceStatus' metaclass collects them already
        if descriptors := getattr(obj, "_descriptors"):  # noqa: B009
            for _name, desc in descriptors.items():
                self.add_descriptor(desc)

        # 2. Check if object members have descriptors
        for _name, method in getmembers(obj, lambda o: hasattr(o, "_descriptor")):
            prop_desc = method._descriptor
            if not isinstance(prop_desc, Descriptor):
                _LOGGER.warning("%s %s is not a descriptor, skipping", _name, method)
                continue

            prop_desc.method = method
            self.add_descriptor(prop_desc)

    def add_descriptor(self, descriptor: Descriptor):
        """Add a descriptor to the collection.

        This adds a suffix to the identifier if the name already exists.
        """
        if not isinstance(descriptor, Descriptor):
            raise TypeError("Tried to add non-descriptor descriptor: %s", descriptor)

        if descriptor.id in self.data:
            descriptor.id = descriptor.id + "-2"
            _LOGGER.warning("Appended '-2' to the id of %s", descriptor)
            # TODO: append suffix to dupe ids
            raise ValueError(f"Duplicate descriptor id: {descriptor.id}")

        if isinstance(descriptor, PropertyDescriptor):
            self._handle_property_descriptor(descriptor)
        elif isinstance(descriptor, ActionDescriptor):
            self._handle_action_descriptor(descriptor)
        else:
            _LOGGER.debug("Using descriptor as is: %s", descriptor)

        self.data[descriptor.id] = descriptor
        _LOGGER.debug("Added descriptor: %r", descriptor)

    def _handle_action_descriptor(self, prop: ActionDescriptor) -> None:
        """Bind the action method to the action."""
        if prop.method_name is not None:
            prop.method = getattr(self._device, prop.method_name)

        if prop.method is None:
            raise Exception(f"Neither method or method_name was defined for {prop}")

    def _handle_property_descriptor(self, prop: PropertyDescriptor) -> None:
        """Bind the setter method to the property."""
        if prop.setter_name is not None:
            prop.setter = getattr(self._device, prop.setter_name)

        if prop.access & AccessFlags.Write and prop.setter is None:
            raise Exception(f"Neither setter or setter_name was defined for {prop}")

        self._handle_constraints(prop)

    def _handle_constraints(self, prop: PropertyDescriptor) -> None:
        """Set attribute-based constraints for the descriptor."""
        if prop.constraint == PropertyConstraint.Choice:
            prop = cast(EnumDescriptor, prop)
            if prop.choices_attribute is not None:
                retrieve_choices_function = getattr(
                    self._device, prop.choices_attribute
                )
                prop.choices = retrieve_choices_function()

        elif prop.constraint == PropertyConstraint.Range:
            prop = cast(RangeDescriptor, prop)
            if prop.range_attribute is not None:
                range_def = getattr(self._device, prop.range_attribute)
                prop.min_value = range_def.min_value
                prop.max_value = range_def.max_value
                prop.step = range_def.step

        # A property without constraints, nothing to do here.

    @property
    def __cli_output__(self):
        """Return a string presentation for the cli."""
        s = ""
        for d in self.data.values():
            s += f"{d.__cli_output__}\n"
        return s
