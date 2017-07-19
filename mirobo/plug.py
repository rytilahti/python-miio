from .device import Device

PROPERTY_POWER = 'power'
PROPERTY_TEMPERATURE = 'temperature'
PROPERTY_CURRENT = 'current'


class Plug(Device):
    """Main class representing the smart wifi socket / plug."""

    def __init__(self, ip: str, token: str, start_id: int = 0, debug: int = 0) -> None:
        super().__init__(ip, token, start_id, debug)
        self.manual_seqnum = -1

    def start(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def stop(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def status(self):
        """Retrieve properties."""
        status =  self.send(
            "get_prop",
            [ PROPERTY_POWER, PROPERTY_TEMPERATURE, PROPERTY_CURRENT ]
        )
        return {
            PROPERTY_POWER: status[0],
            PROPERTY_TEMPERATURE: status[1],
            PROPERTY_CURRENT: status[2]
        }

    def raw_command(self, cmd, params):
        """Send a raw command to the device."""
        return self.send(cmd, params)
