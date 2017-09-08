import logging
from typing import Any, Dict
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class WaterPurifier(Device):
    """Main class representing the waiter purifier."""

    def status(self):
        """Retrieve properties."""

        properties = ['power']

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

        return WaterPurifierStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])


class WaterPurifierStatus:
    """Container for status reports from the water purifier."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    def __str__(self) -> str:
        return "<WaterPurifierStatus power=%s>" % self.power
