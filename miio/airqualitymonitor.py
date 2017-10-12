import logging
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class AirQualityMonitorStatus:
    def __init__(self, data):
        # ['power': 'on', 'aqi': 34, 'battery': 0, 'usb_state': 'on']
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def usb_power(self) -> bool:
        return self.data["usb_state"] == "on"

    @property
    def aqi(self) -> int:
        return self.data["aqi"]

    @property
    def battery(self) -> int:
        return self.data["battery"]


class AirQualityMonitor(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def status(self):
        """Return device status."""

        properties = ['power', 'aqi', 'battery', 'usb_state']

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

        return AirQualityMonitorStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])
