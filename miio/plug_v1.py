import logging
from typing import Dict, Any
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)

class PlugV1Status:
    """Container for status reports from the plug."""

    def __init__(self, data: Dict[str, Any]) -> None:
        # { 'power': True, 'usb_on': True, 'temperature': 32 }
        self.data = data

    @property
    def power(self) -> bool:
        """Current power state."""
        return self.data["on"]

    @property
    def is_on(self) -> bool:
        """True if device is on."""
        return self.power

    @property
    def usb_power(self) -> bool:
        """True if USB is on."""
        return self.data["usb_on"]

    @property
    def temperature(self) -> float:
        return self.data["temperature"]

    def __str__(self) -> str:
        s = "<PlugV1Status power=%s, usb_power=%s, temperature=%s>" % \
            (self.power,
             self.usb_power,
             self.temperature)
        return s


class PlugV1(Device):
    """Main class representing the chuangmi plug v1."""

    def status(self) -> PlugV1Status:
        """Retrieve properties."""
        properties = ['on', 'usb_on', 'temperature']
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

        return PlugV1Status(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_on", [])

    def off(self):
        """Power off."""
        return self.send("set_off", [])

    def usb_on(self):
        """Power on."""
        return self.send("set_usb_on", [])

    def usb_off(self):
        """Power off."""
        return self.send("set_usb_off", [])
