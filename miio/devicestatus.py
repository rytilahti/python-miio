import inspect
import logging
import warnings
from typing import Dict, Union, get_args, get_origin, get_type_hints

from .descriptors import SensorDescriptor, SwitchDescriptor

_LOGGER = logging.getLogger(__name__)


class _StatusMeta(type):
    """Meta class to provide introspectable properties."""

    def __new__(metacls, name, bases, namespace, **kwargs):
        cls = super().__new__(metacls, name, bases, namespace)
        cls._sensors: Dict[str, SensorDescriptor] = {}
        cls._switches: Dict[str, SwitchDescriptor] = {}
        for n in namespace:
            prop = getattr(namespace[n], "fget", None)
            if prop:
                sensor = getattr(prop, "_sensor", None)
                if sensor:
                    _LOGGER.debug(f"Found sensor: {sensor} for {name}")
                    cls._sensors[n] = sensor

                switch = getattr(prop, "_switch", None)
                if switch:
                    _LOGGER.debug(f"Found switch {switch} for {name}")
                    cls._switches[n] = switch

        return cls


class DeviceStatus(metaclass=_StatusMeta):
    """Base class for status containers.

    All status container classes should inherit from this class:

    * This class allows downstream users to access the available information in an
      introspectable way.
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


def sensor(*, name: str, unit: str = "", **kwargs):
    """Syntactic sugar to create SensorDescriptor objects.

    The information can be used by users of the library to programatically find out what
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


def switch(*, name: str, setter_name: str, **kwargs):
    """Syntactic sugar to create SwitchDescriptor objects.

    The information can be used by users of the library to programatically find out what
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
