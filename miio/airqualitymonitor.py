import logging
from collections import defaultdict

import click

from .click_common import command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRQUALITYMONITOR_V1 = 'zhimi.airmonitor.v1'
MODEL_AIRQUALITYMONITOR_B1 = 'cgllc.airmonitor.b1'
MODEL_AIRQUALITYMONITOR_S1 = 'cgllc.airmonitor.s1'

AVAILABLE_PROPERTIES_COMMON = [
    'power', 'aqi', 'battery', 'usb_state', 'time_state',
    'night_state', 'night_beg_time', 'night_end_time',
    'sensor_state'
]

AVAILABLE_PROPERTIES_S1 = [
    'battery', 'co2', 'humidity', 'pm25', 'temperature', 'tvoc'
]

AVAILABLE_PROPERTIES = {
    MODEL_AIRQUALITYMONITOR_V1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_AIRQUALITYMONITOR_B1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_AIRQUALITYMONITOR_S1: AVAILABLE_PROPERTIES_S1,
}


class AirQualityMonitorException(DeviceException):
    pass


class AirQualityMonitorStatus:
    """Container of air quality monitor status."""

    def __init__(self, data):
        """
        Response of a Xiaomi Air Quality Monitor (zhimi.airmonitor.v1):

        {'power': 'on', 'aqi': 34, 'battery': 100, 'usb_state': 'off', 'time_state': 'on'}

        Response of a Xiaomi Air Quality Monitor (cgllc.airmonitor.b1):

        unknown.

        Response of a Xiaomi Air Quality Monitor (cgllc.airmonitor.s1):

        {'battery': 100, 'co2': 695, 'humidity': 62.1, 'pm25': 19.4, 'temperature': 27.4,
         'tvoc': 254}
        """
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

    @property
    def co2(self) -> int:
        """Return co2 value (400...9999)ppm for MODEL_AIRQUALITYMONITOR_S1."""
        return self.data["co2"]

    @property
    def humidity(self) -> float:
        """Return humidity value (0...100)% for MODEL_AIRQUALITYMONITOR_S1."""
        return self.data["humidity"]

    @property
    def pm25(self) -> float:
        """Return pm2.5 value (0...999)μg/m³ for MODEL_AIRQUALITYMONITOR_S1."""
        return self.data["pm25"]

    @property
    def temperature(self) -> float:
        """Return temperature value (-10...50)°C for MODEL_AIRQUALITYMONITOR_S1."""
        return self.data["temperature"]

    @property
    def tvoc(self) -> int:
        """Return tvoc value for MODEL_AIRQUALITYMONITOR_S1."""
        return self.data["tvoc"]

    def __repr__(self) -> str:
        s = "<AirQualityMonitorStatus power=%s, " \
            "aqi=%s, " \
            "battery=%s, " \
            "usb_power=%s, " \
            "temperature=%s, " \
            "humidity=%s, " \
            "co2=%s, " \
            "pm2.5=%s, " \
            "tvoc=%s, " \
            "display_clock=%s>" % \
            (self.power,
             self.aqi,
             self.battery,
             self.usb_power,
             self.temperature,
             self.humidity,
             self.co2,
             self.pm25,
             self.tvoc,
             self.display_clock)
        return s

    def __json__(self):
        return self.data


class AirQualityMonitor(Device):
    """Xiaomi PM2.5 Air Quality Monitor."""
    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = None) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        self.device_info = self.info()
        if self.device_info and model is None:
            model = self.device_info.model

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_AIRQUALITYMONITOR_V1
            _LOGGER.error("Device model %s unsupported. Falling back to %s.", model, self.model)

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "USB power: {result.usb_power}\n"
            "AQI: {result.aqi}\n"
            "Battery: {result.battery}\n"
            "Display clock: {result.display_clock}\n"
        )
    )
    def status(self) -> AirQualityMonitorStatus:
        """Return device status."""

        properties = AVAILABLE_PROPERTIES[self.model]

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

        if self.model == MODEL_AIRQUALITYMONITOR_S1:
            return AirQualityMonitorStatus(defaultdict(lambda: None, values))
        else:
            return AirQualityMonitorStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering off"),
    )
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("display_clock", type=bool),
        default_output=format_output(
            lambda led: "Turning on display clock"
            if led else "Turning off display clock"
        )
    )
    def set_display_clock(self, display_clock: bool):
        """Enable/disable displaying a clock instead the AQI."""
        if display_clock:
            self.send("set_time_state", ["on"])
        else:
            self.send("set_time_state", ["off"])

    @command(
        click.argument("auto_close", type=bool),
        default_output=format_output(
            lambda led: "Turning on auto close"
            if led else "Turning off auto close"
        )
    )
    def set_auto_close(self, auto_close: bool):
        """Purpose unknown."""
        if auto_close:
            self.send("set_auto_close", ["on"])
        else:
            self.send("set_auto_close", ["off"])

    @command(
        click.argument("night_mode", type=bool),
        default_output=format_output(
            lambda led: "Turning on night mode"
            if led else "Turning off night mode"
        )
    )
    def set_night_mode(self, night_mode: bool):
        """Decrease the brightness of the display."""
        if night_mode:
            self.send("set_night_state", ["on"])
        else:
            self.send("set_night_state", ["off"])

    @command(
        click.argument("begin_hour", type=int),
        click.argument("begin_minute", type=int),
        click.argument("end_hour", type=int),
        click.argument("end_minute", type=int),
        default_output=format_output(
            "Setting night time to {begin_hour}:{begin_minute} - {end_hour}:{end_minute}")
    )
    def set_night_time(self, begin_hour: int, begin_minute: int,
                       end_hour: int, end_minute: int):
        """Enable night mode daily at bedtime."""
        begin = begin_hour * 3600 + begin_minute * 60
        end = end_hour * 3600 + end_minute * 60

        if begin < 0 or begin > 86399 or end < 0 or end > 86399:
            AirQualityMonitorException("Begin or/and end time invalid.")

        self.send("set_night_time", [begin, end])
