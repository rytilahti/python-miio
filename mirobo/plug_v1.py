from .device import Device
from .containers import PlugV1Status


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
