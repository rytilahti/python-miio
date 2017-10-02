import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class PlugStatus:
    """Container for status reports from the plug."""
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def temperature(self) -> float:
        return self.data["temperature"]

    @property
    def load_power(self) -> Optional[float]:
        if self.data["current"] is not None:
            # The constant of 110V is used intentionally. The current was
            # calculated with a wrong reference voltage already.
            return self.data["current"] * 110
        return None

    def __str__(self) -> str:
        s = "<PlugStatus power=%s, temperature=%s, load_power=%s>" % \
            (self.power,
             self.temperature,
             self.load_power)
        return s


class Plug(Device):
    """Main class representing the smart wifi socket / plug."""

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def status(self):
        """Retrieve properties."""
        properties = ['power', 'temperature', 'current']
        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return PlugStatus(
            defaultdict(lambda: None, zip(properties, values)))
