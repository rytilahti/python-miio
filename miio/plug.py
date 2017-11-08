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
        """Power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """Return True if the device is on."""
        return self.power == "on"

    @property
    def temperature(self) -> float:
        """Return temperature."""
        return self.data["temperature"]

    def __str__(self) -> str:
        s = "<PlugStatus power=%s, temperature=%s>" % \
            (self.power,
             self.temperature)
        return s


class Plug(Device):
    """Main class representing the smart wifi socket / plug."""

    def status(self) -> PlugStatus:
        """Retrieve properties."""
        properties = ['power', 'temperature']
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

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])
