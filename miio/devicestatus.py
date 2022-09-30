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

from .descriptors import (
    EnumSettingDescriptor,
    NumberSettingDescriptor,
    SensorDescriptor,
    SettingDescriptor,
    SwitchDescriptor,
)

_LOGGER = logging.getLogger(__name__)


class _StatusMeta(type):
    """Meta class to provide introspectable properties."""

    def __new__(metacls, name, bases, namespace, **kwargs):
        cls = super().__new__(metacls, name, bases, namespace)

        # TODO: clean up to contain all of these in a single container
        cls._sensors: Dict[str, SensorDescriptor] = {}
        cls._switches: Dict[str, SwitchDescriptor] = {}
        cls._settings: Dict[str, SettingDescriptor] = {}

        cls._embedded: Dict[str, "DeviceStatus"] = {}

        descriptor_map = {
            "sensor": cls._sensors,
            "switch": cls._switches,
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
      introspectable way. See :func:`@property`, :func:`switch`, and :func:`@setting`.
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

    def switches(self) -> Dict[str, SwitchDescriptor]:
        """Return the dict of sensors exposed by the status container.

        You can use @sensor decorator to define sensors inside your status class.
        """
        return self._switches  # type: ignore[attr-defined]

    def settings(self) -> Dict[str, SettingDescriptor]:
        """Return the dict of settings exposed by the status container.

        You can use @setting decorator to define sensors inside your status class.
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
        setattr(self, other_name, other)

        for name, sensor in other.sensors().items():
            final_name = f"{other_name}:{name}"
            import attr

            self._sensors[final_name] = attr.evolve(sensor, property=final_name)

        for name, switch in other.switches().items():
            final_name = f"{other_name}:{name}"
            self._switches[final_name] = attr.evolve(switch, property=final_name)

        for name, setting in other.settings().items():
            final_name = f"{other_name}:{name}"
            self._settings[final_name] = attr.evolve(setting, property=final_name)


def sensor(name: str, *, unit: str = "", **kwargs):
    """Syntactic sugar to create SensorDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of sensors are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.SensorDescriptor.extras`,
    and can be interpreted downstream users as they wish.
    """

    def decorator_sensor(func):
        property_name = func.__name__

        def _sensor_type_for_return_type(func):
            rtype = get_type_hints(func).get("return")
            if get_origin(rtype) is Union:  # Unwrap Optional[]
                rtype, _ = get_args(rtype)

            if rtype == bool:
                return "binary"
            else:
                return "sensor"

        sensor_type = _sensor_type_for_return_type(func)
        descriptor = SensorDescriptor(
            id=str(property_name),
            property=str(property_name),
            name=name,
            unit=unit,
            type=sensor_type,
            extras=kwargs,
        )
        func._sensor = descriptor

        return func

    return decorator_sensor


def switch(name: str, *, setter_name: str, **kwargs):
    """Syntactic sugar to create SwitchDescriptor objects.

    The information can be used by users of the library to programmatically find out what
    types of sensors are available for the device.

    The interface is kept minimal, but you can pass any extra keyword arguments.
    These extras are made accessible over :attr:`~miio.descriptors.SwitchDescriptor.extras`,
    and can be interpreted downstream users as they wish.
    """

    def decorator_sensor(func):
        property_name = func.__name__

        descriptor = SwitchDescriptor(
            id=str(property_name),
            property=str(property_name),
            name=name,
            setter_name=setter_name,
            extras=kwargs,
        )
        func._switch = descriptor

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
    """

    def decorator_setting(func):
        property_name = func.__name__

        if setter is None and setter_name is None:
            raise Exception("Either setter or setter_name needs to be defined")

        if min_value or max_value:
            descriptor = NumberSettingDescriptor(
                id=str(property_name),
                property=str(property_name),
                name=name,
                unit=unit,
                setter=setter,
                setter_name=setter_name,
                min_value=min_value or 0,
                max_value=max_value,
                step=step or 1,
                extras=kwargs,
            )
        elif choices or choices_attribute:
            if choices_attribute is not None:
                # TODO: adding choices from attribute is a bit more complex, as it requires a way to
                # construct enums pointed by the attribute
                raise NotImplementedError("choices_attribute is not yet implemented")
            descriptor = EnumSettingDescriptor(
                id=str(property_name),
                property=str(property_name),
                name=name,
                unit=unit,
                setter=setter,
                setter_name=setter_name,
                choices=choices,
                choices_attribute=choices_attribute,
                extras=kwargs,
            )
        else:
            raise Exception(
                "Neither {min,max}_value or choices_{attribute} was defined"
            )

        func._setting = descriptor

        return func

    return decorator_setting
