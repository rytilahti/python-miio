import logging

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)

class XiaomiGatewayAlarm(Device):
    """Main class representing the Xiaomi Gateway Alarm."""

    def __init__(self, Device) -> None:
        self._device = Device

    @command(
        default_output=format_output("[alarm_status]"))
    def status(self):
        """Fetch alarm status from the device."""
        # Response: ['on'], ['off'], ['oning']
        alarm_status = self._device.send("get_arming") 

        return alarm_status

    @command(default_output=format_output("Turning alarm on"))
    def alarm_on(self):
        """Turning alarm on."""
        return self._device.send("set_arming", ["on"])

    @command(default_output=format_output("Turning alarm off"))
    def alarm_off(self):
        """Turning alarm off."""
        return self._device.send("set_arming", ["off"])
