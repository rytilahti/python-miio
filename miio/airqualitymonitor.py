import logging
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)


class AirQualityMonitorStatus:
    """Container of air quality monitor status."""
    def __init__(self, data):
        # {'power': 'on', 'aqi': 34, 'battery': 100, 'usb_state': 'off'}
        self.data = data

    @property
    def power(self) -> str:
        """Current power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """Return True if the device is turned on."""
        return self.power == "on"

    @property
    def usb_power(self) -> bool:
        """Return True if the device's usb is on."""
        return self.data["usb_state"] == "on"

    @property
    def aqi(self) -> int:
        """Air quality index value. (0...600)."""
        return self.data["aqi"]

    @property
    def battery(self) -> int:
        """Current battery level (0...100)."""
        return self.data["battery"]

    @property
    def time_state(self) -> str:
        """Current time state."""
        return self.data["time_state"]

    def __repr__(self) -> str:
        s = "<AirQualityMonitorStatus power=%s, " \
            "aqi=%s, " \
            "battery=%s, " \
            "usb_power=%s, " \
            "time_state=%s>" % \
            (self.power,
             self.aqi,
             self.battery,
             self.usb_power,
             self.time_state)
        return s


class AirQualityMonitor(Device):
    """Xiaomi PM2.5 Air Quality Monitor."""
    def status(self) -> AirQualityMonitorStatus:
        """Return device status."""

        properties = ['power', 'aqi', 'battery', 'usb_state', 'time_state']

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
