from .device import Device
from .containers import PlugStatus


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
