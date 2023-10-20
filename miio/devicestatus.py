import inspect
import logging
import warnings
from enum import Enum
from typing import (
    Callable,
    Dict,
    Iterable,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import attr

from .descriptors import (
    AccessFlags,
    ActionDescriptor,
    EnumDescriptor,
    PropertyDescriptor,
    RangeDescriptor,
)
from .identifiers import StandardIdentifier

_LOGGER = logging.getLogger(__name__)


class _StatusMeta(type):
    """Meta class to provide introspectable properties."""

    def __new__(metacls, name, bases, namespace, **kwargs):
        cls = super().__new__(metacls, name, bases, namespace)

        cls._descriptors: Dict[str, PropertyDescriptor] = {}
        cls._parent: Optional["DeviceStatus"] = None
        cls._embedded: Dict[str, "DeviceStatus"] = {}

        for n in namespace:
            prop = getattr(namespace[n], "fget", None)
            if prop:
                descriptor = getattr(prop, "_descriptor", None)
                if descriptor:
                    _LOGGER.debug(f"Found descriptor for {name} {descriptor}")
                    if n in cls._descriptors:
                        raise ValueError(f"Duplicate {n} for {name} {descriptor}")
                    cls._descriptors[n] = descriptor
                    _LOGGER.debug("Created %s.%s: %s", name, n, descriptor)

        return cls


class DeviceStatus(metaclass=_StatusMeta):
    """Base class for status containers.

    All status container classes should inherit from this class:

    * This class allows downstream users to access the available information in an
      introspectable way. See :func:`@sensor` and :func:`@setting`.
    * :func:`embed` allows embedding other status containers.
    * The __repr__ implementation returns all defined properties and their values.
    """

    def __repr__(self):
        props = inspect.getmembers(self.__class__, lambda o: isinstance(o, property))

        s = f"<{self.__class__.__name__}"
        for prop_tuple in props:
            name, prop = prop_tuple
            if name.startswith("_"):  # skip internals
                continue
            try:
                # ignore deprecation warnings
                with warnings.catch_warnings(record=True):
                    prop_value = prop.fget(self)
            except Exception as ex:
                prop_value = ex.__class__.__name__

            s += f" {name}={prop_value}"

        for name, embedded in self._embedded.items():
            s += f" {name}={repr(embedded)}"

        s += ">"
        return s

    def properties(self) -> Dict[str, PropertyDescriptor]:
        """Return the dict of sensors exposed by the status container.

        Use @sensor and @setting decorators to define properties.
        """
        return self._descriptors  # type: ignore[attr-defined]

    def settings(self) -> Dict[str, PropertyDescriptor]:
        """Return the dict of settings exposed by the status container.

        This is just a dict of writable properties, see :meth:`properties`.
        """
        # TODO: this is not probably worth having, remove?
        return {
            prop.id: prop
            for prop in self.properties().values()
            if prop.access & AccessFlags.Write
        }

    def embed(self, name: str, other: "DeviceStatus"):
        """Embed another status container to current one.

        This makes it easy to provide a single status response for cases where responses
        from multiple I/O calls is wanted to provide a simple interface for downstreams.

        Internally, this will prepend the name of the other class to the attribute names,
        and override the __getattribute__ to lookup attributes in the embedded containers.
        """
        self._embedded[name] = other
        other._parent = self  # type: ignore[attr-defined]

        for property_name, prop in other.properties().items():
            final_name = f"{name}__{property_name}"

            self._descriptors[final_name] = attr.evolve(
                prop, status_attribute=final_name
            )

    def __dir__(self) -> Iterable[str]:
        """Overridden to include properties from embedded containers."""
        return list(super().__dir__()) + list(self._embedded) + list(self._descriptors)

    @property
    def __cli_output__(self) -> str:
        """Return a CLI formatted output of the status."""
        out = ""
        for descriptor in self.properties().values():
            try:
                value = getattr(self, descriptor.status_attribute)
            except KeyError:
                continue  # skip missing properties

            if value is None:  # skip none values
                _LOGGER.debug("Skipping %s because it's None", descriptor.name)
                continue

            out += f"{descriptor.access} {descriptor.name} ({descriptor.id}): {value}"

            if descriptor.unit is not None:
                out += f" {descriptor.unit}"

            out += "\n"

        return out

    def __getattr__(self, item):
        """Overridden to lookup properties from embedded containers."""
        if item.startswith("__") and item.endswith("__"):
            return super().__getattribute__(item)

        if item in self._embedded:
            return self._embedded[item]

        if "__" not in item:
            return super().__getattribute__(item)

        embed, prop = item.split("__", maxsplit=1)
        if not embed or not prop:
            return super().__getattribute__(item)

        return getattr(self._embedded[embed], prop)


def _get_qualified_name(func, id_: Optional[Union[str, StandardIdentifier]]):
    """Return qualified name for a descriptor identifier."""
    if id_ is not None and isinstance(id_, StandardIdentifier):
        return str(id_.value)
    return id_ or str(func.__qualname__)


def _sensor_type_for_return_type(func):
    """Return the return type for a method from its type hint."""
    rtype = get_type_hints(func).get("return")
    if get_origin(rtype) is Union:  # Unwrap Optional[]
        rtype, _ = get_args(rtype)

    return rtype


def sensor(
    name: str,
    *,
    id: Optional[Union[str, StandardIdentifier]] = None,
    unit: Optional[str] = None,
    **kwargs,
):
    """Syntactic sugar to create SensorDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of sensors are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.SensorDescriptor.extras`,
    and can be interpreted downstream users as they wish.
    """

    def decorator_sensor(func):
        func_name = str(func.__name__)
        qualified_name = _get_qualified_name(func, id)

        sensor_type = _sensor_type_for_return_type(func)
        descriptor = PropertyDescriptor(
            id=qualified_name,
            status_attribute=func_name,
            name=name,
            unit=unit,
            type=sensor_type,
            extras=kwargs,
        )
        func._descriptor = descriptor

        return func

    return decorator_sensor


def setting(
    name: str,
    *,
    id: Optional[Union[str, StandardIdentifier]] = None,
    setter: Optional[Callable] = None,
    setter_name: Optional[str] = None,
    unit: Optional[str] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    step: Optional[int] = None,
    range_attribute: Optional[str] = None,
    choices: Optional[Type[Enum]] = None,
    choices_attribute: Optional[str] = None,
    **kwargs,
):
    """Syntactic sugar to create SettingDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of sensors are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.SettingDescriptor.extras`,
    and can be interpreted downstream users as they wish.

    The `_attribute` suffixed options allow defining a property to be used to return the information dynamically.
    """

    def decorator_setting(func):
        func_name = str(func.__name__)
        qualified_name = _get_qualified_name(func, id)

        if setter is None and setter_name is None:
            raise Exception("setter_name needs to be defined")

        common_values = {
            "id": qualified_name,
            "status_attribute": func_name,
            "name": name,
            "unit": unit,
            "setter": setter,
            "setter_name": setter_name,
            "extras": kwargs,
            "type": _sensor_type_for_return_type(func),
            "access": AccessFlags.Read | AccessFlags.Write,
        }

        if min_value or max_value or range_attribute:
            descriptor = RangeDescriptor(
                **common_values,
                min_value=min_value or 0,
                max_value=max_value,
                step=step or 1,
                range_attribute=range_attribute,
            )
        elif choices or choices_attribute:
            descriptor = EnumDescriptor(
                **common_values,
                choices=choices,
                choices_attribute=choices_attribute,
            )
        else:
            descriptor = PropertyDescriptor(**common_values)

        func._descriptor = descriptor

        return func

    return decorator_setting


def action(name: str, *, id: Optional[Union[str, StandardIdentifier]] = None, **kwargs):
    """Syntactic sugar to create ActionDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of actions are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.ActionDescriptor.extras`,
    and can be interpreted downstream users as they wish.
    """

    def decorator_action(func):
        func_name = str(func.__name__)
        qualified_name = _get_qualified_name(func, id)

        descriptor = ActionDescriptor(
            id=qualified_name,
            name=name,
            method_name=func_name,
            method=None,
            extras=kwargs,
        )
        func._descriptor = descriptor

        return func

    return decorator_action
