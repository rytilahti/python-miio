import logging
from collections import defaultdict

from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)


class AirQualityMonitorException(DeviceException):
    pass


class AirQualityMonitorStatus:
    """Container of air quality monitor status."""

    def __init__(self, data):
        # {'power': 'on', 'aqi': 34, 'battery': 100, 'usb_state': 'off', 'time_state': 'on'}
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
    def display_clock(self) -> bool:
        """Display a clock instead the AQI."""
        return self.data["time_state"] == "on"

    @property
    def night_mode(self) -> bool:
        """Return True if the night mode is on."""
        return self.data["night_state"] == "on"

    @property
    def night_time_begin(self) -> str:
        """Return the begin of the night time."""
        return self.data["night_beg_time"]

    @property
    def night_time_end(self) -> str:
        """Return the end of the night time."""
        return self.data["night_end_time"]

    @property
    def sensor_state(self) -> str:
        """Sensor state."""
        return self.data["sensor_state"]

    def __repr__(self) -> str:
        s = "<AirQualityMonitorStatus power=%s, " \
            "aqi=%s, " \
            "battery=%s, " \
            "usb_power=%s, " \
            "display_clock=%s>" % \
            (self.power,
             self.aqi,
             self.battery,
             self.usb_power,
             self.display_clock)
        return s


class AirQualityMonitor(Device):
    """Xiaomi PM2.5 Air Quality Monitor."""

    def status(self) -> AirQualityMonitorStatus:
        """Return device status."""

        properties = ['power', 'aqi', 'battery', 'usb_state', 'time_state',
                      'night_state', 'night_beg_time', 'night_end_time',
                      'sensor_state']

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

    def set_display_clock(self, display_clock: bool):
        """Enable/disable displaying a clock instead the AQI."""
        if display_clock:
            self.send("set_time_state", ["on"])
        else:
            self.send("set_time_state", ["off"])

    def set_auto_close(self, auto_close: bool):
        """Purpose unknown."""
        if auto_close:
            self.send("set_auto_close", ["on"])
        else:
            self.send("set_auto_close", ["off"])

    def set_night_mode(self, night_mode: bool):
        """Decrease the brightness of the display."""
        if night_mode:
            self.send("set_night_state", ["on"])
        else:
            self.send("set_night_state", ["off"])

    def set_night_time(self, begin_hour: int, begin_minute: int,
                       end_hour: int, end_minute: int):
        """Enable night mode daily at bedtime."""
        begin = begin_hour * 3600 + begin_minute * 60
        end = end_hour * 3600 + end_minute * 60

        if begin < 0 or begin > 86399 or end < 0 or end > 86399:
            AirQualityMonitorException("Begin or/and end time invalid.")

        self.send("set_night_time", [begin, end])
