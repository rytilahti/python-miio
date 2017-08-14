from .device import Device
from typing import Any, Dict


class PlugV1(Device):
    """Main class representing the chuangmi plug v1."""

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

    def status(self):
        """Retrieve properties."""
        properties = ['on', 'usb_on']
        values = self.send(
            "get_prop",
            properties
        )
        return PlugV1Status(dict(zip(properties, values)))


class PlugV1Status:
    """Container for status reports from the plug."""
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def power(self) -> bool:
        return self.data["on"]

    @property
    def is_on(self) -> bool:
        return self.power

    @property
    def usb_power(self) -> bool:
        return self.data["usb_on"]

    def __str__(self) -> str:
        s = "<PlugV1Status power=%s, usb_power=%s>" % \
            (self.power,
             self.usb_power)
        return s
