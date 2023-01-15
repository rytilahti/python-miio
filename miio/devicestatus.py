import inspect
import logging
import warnings
from enum import Enum
from typing import (
    Callable,
    Dict,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import attr

from .descriptors import (
    ActionDescriptor,
    BooleanSettingDescriptor,
    EnumSettingDescriptor,
    NumberSettingDescriptor,
    SensorDescriptor,
    SettingDescriptor,
    SettingType,
)

_LOGGER = logging.getLogger(__name__)


class _StatusMeta(type):
    """Meta class to provide introspectable properties."""

    def __new__(metacls, name, bases, namespace, **kwargs):
        cls = super().__new__(metacls, name, bases, namespace)

        # TODO: clean up to contain all of these in a single container
        cls._sensors: Dict[str, SensorDescriptor] = {}
        cls._settings: Dict[str, SettingDescriptor] = {}

        cls._embedded: Dict[str, "DeviceStatus"] = {}

        descriptor_map = {
            "sensor": cls._sensors,
            "setting": cls._settings,
        }
        for n in namespace:
            prop = getattr(namespace[n], "fget", None)
            if prop:
                for type_, container in descriptor_map.items():
                    item = getattr(prop, f"_{type_}", None)
                    if item:
                        _LOGGER.debug(f"Found {type_} for {name} {item}")
                        container[n] = item

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

    def sensors(self) -> Dict[str, SensorDescriptor]:
        """Return the dict of sensors exposed by the status container.

        You can use @sensor decorator to define sensors inside your status class.
        """
        return self._sensors  # type: ignore[attr-defined]

    def settings(self) -> Dict[str, SettingDescriptor]:
        """Return the dict of settings exposed by the status container.

        You can use @setting decorator to define settings inside your status class.
        """
        return self._settings  # type: ignore[attr-defined]

    def embed(self, other: "DeviceStatus"):
        """Embed another status container to current one.

        This makes it easy to provide a single status response for cases where responses
        from multiple I/O calls is wanted to provide a simple interface for downstreams.

        Internally, this will prepend the name of the other class to the property names,
        and override the __getattribute__ to lookup attributes in the embedded containers.
        """
        other_name = str(other.__class__.__name__)

        self._embedded[other_name] = other

        for name, sensor in other.sensors().items():
            final_name = f"{other_name}__{name}"

            self._sensors[final_name] = attr.evolve(sensor, property=final_name)

        for name, setting in other.settings().items():
            final_name = f"{other_name}__{name}"
            self._settings[final_name] = attr.evolve(setting, property=final_name)

    def __getattr__(self, item):
        """Overridden to lookup properties from embedded containers."""
        if item.startswith("__") and item.endswith("__"):
            return super().__getattribute__(item)

        embed, prop = item.split("__", maxsplit=1)
        if not embed or not prop:
            return super().__getattribute__(item)

        return getattr(self._embedded[embed], prop)


def sensor(name: str, *, unit: Optional[str] = None, **kwargs):
    """Syntactic sugar to create SensorDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of sensors are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.SensorDescriptor.extras`,
    and can be interpreted downstream users as they wish.
    """

    def decorator_sensor(func):
        property_name = str(func.__name__)
        qualified_name = str(func.__qualname__)

        def _sensor_type_for_return_type(func):
            rtype = get_type_hints(func).get("return")
            if get_origin(rtype) is Union:  # Unwrap Optional[]
                rtype, _ = get_args(rtype)

            return rtype

        sensor_type = _sensor_type_for_return_type(func)
        descriptor = SensorDescriptor(
            id=qualified_name,
            property=property_name,
            name=name,
            unit=unit,
            type=sensor_type,
            extras=kwargs,
        )
        func._sensor = descriptor

        return func

    return decorator_sensor


def setting(
    name: str,
    *,
    setter: Optional[Callable] = None,
    setter_name: Optional[str] = None,
    unit: Optional[str] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    step: Optional[int] = None,
    range_attribute: Optional[str] = None,
    choices: Optional[Type[Enum]] = None,
    choices_attribute: Optional[str] = None,
    type: Optional[SettingType] = None,
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
        property_name = str(func.__name__)
        qualified_name = str(func.__qualname__)

        if setter is None and setter_name is None:
            raise Exception("setter_name needs to be defined")
        if setter_name is None:
            raise NotImplementedError(
                "setter not yet implemented, use setter_name instead"
            )

        common_values = {
            "id": qualified_name,
            "property": property_name,
            "name": name,
            "unit": unit,
            "setter": setter,
            "setter_name": setter_name,
            "extras": kwargs,
        }

        if min_value or max_value or range_attribute:
            descriptor = NumberSettingDescriptor(
                **common_values,
                min_value=min_value or 0,
                max_value=max_value,
                step=step or 1,
                range_attribute=range_attribute,
            )
        elif choices or choices_attribute:
            descriptor = EnumSettingDescriptor(
                **common_values,
                choices=choices,
                choices_attribute=choices_attribute,
            )
        else:
            descriptor = BooleanSettingDescriptor(**common_values)

        func._setting = descriptor

        return func

    return decorator_setting


def action(name: str, **kwargs):
    """Syntactic sugar to create ActionDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of actions are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.ActionDescriptor.extras`,
    and can be interpreted downstream users as they wish.
    """

    def decorator_action(func):
        property_name = str(func.__name__)
        qualified_name = str(func.__qualname__)

        descriptor = ActionDescriptor(
            id=qualified_name,
            name=name,
            method_name=property_name,
            method=None,
            extras=kwargs,
        )
        func._action = descriptor

        return func

    return decorator_action
