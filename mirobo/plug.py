from .device import Device
from typing import Dict, Any


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
    def current(self) -> float:
        return self.data["current"]

    def __str__(self) -> str:
        s = "<PlugStatus power=%s, temperature=%s, current=%s>" % \
            (self.power,
             self.temperature,
             self.current)
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
        return PlugStatus(dict(zip(properties, values)))
