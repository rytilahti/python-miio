from .device import Device
from .containers import StripStatus


class Strip(Device):
    """Main class representing the smart strip."""

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def status(self):
        """Retrieve properties."""
        properties = ['power', 'temperature', 'current', 'mode']
        values = self.send(
            "get_prop",
            properties
        )
        return StripStatus(dict(zip(properties, values)))

    def set_power_mode(self, mode: str):
        """Set mode."""

        # green, normal
        return self.send("set_power_mode", [mode])
