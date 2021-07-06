import logging
from collections import defaultdict
from typing import Optional

import click

from .click_common import command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRQUALITYMONITOR_V1 = "zhimi.airmonitor.v1"
MODEL_AIRQUALITYMONITOR_B1 = "cgllc.airmonitor.b1"
MODEL_AIRQUALITYMONITOR_S1 = "cgllc.airmonitor.s1"

AVAILABLE_PROPERTIES_COMMON = [
    "power",
    "aqi",
    "battery",
    "usb_state",
    "time_state",
    "night_state",
    "night_beg_time",
    "night_end_time",
    "sensor_state",
]

AVAILABLE_PROPERTIES_B1 = ["co2e", "humidity", "pm25", "temperature", "tvoc"]

AVAILABLE_PROPERTIES_S1 = ["battery", "co2", "humidity", "pm25", "temperature", "tvoc"]

AVAILABLE_PROPERTIES = {
    MODEL_AIRQUALITYMONITOR_V1: AVAILABLE_PROPERTIES_COMMON,
    MODEL_AIRQUALITYMONITOR_B1: AVAILABLE_PROPERTIES_B1,
    MODEL_AIRQUALITYMONITOR_S1: AVAILABLE_PROPERTIES_S1,
}


class AirQualityMonitorException(DeviceException):
    pass


class AirQualityMonitorStatus(DeviceStatus):
    """Container of air quality monitor status."""

    def __init__(self, data):
        """Response of a Xiaomi Air Quality Monitor (zhimi.airmonitor.v1):

        {'power': 'on', 'aqi': 34, 'battery': 100, 'usb_state': 'off', 'time_state': 'on'}

        Response of a Xiaomi Air Quality Monitor (cgllc.airmonitor.b1):

        {'co2e': 1466, 'humidity': 59.79999923706055, 'pm25': 2, 'temperature': 19.799999237060547,
         'temperature_unit': 'c', 'tvoc': 1.3948699235916138, 'tvoc_unit': 'mg_m3'}

        Response of a Xiaomi Air Quality Monitor (cgllc.airmonitor.s1):

        {'battery': 100, 'co2': 695, 'humidity': 62.1, 'pm25': 19.4, 'temperature': 27.4,
         'tvoc': 254}
        """
        self.data = data

    @property
    def power(self) -> Optional[str]:
        """Current power state."""
        return self.data.get("power", None)

    @property
    def is_on(self) -> bool:
        """Return True if the device is turned on."""
        return self.power == "on"

    @property
    def usb_power(self) -> Optional[bool]:
        """Return True if the device's usb is on."""
        if "usb_state" in self.data and self.data["usb_state"] is not None:
            return self.data["usb_state"] == "on"
        return None

    @property
    def aqi(self) -> Optional[int]:
        """Air quality index value (0..600)."""
        return self.data.get("aqi", None)

    @property
    def battery(self) -> Optional[int]:
        """Current battery level (0..100)."""
        return self.data.get("battery", None)

    @property
    def display_clock(self) -> Optional[bool]:
        """Display a clock instead the AQI."""
        if "time_state" in self.data and self.data["time_state"] is not None:
            return self.data["time_state"] == "on"
        return None

    @property
    def night_mode(self) -> Optional[bool]:
        """Return True if the night mode is on."""
        if "night_state" in self.data and self.data["night_state"] is not None:
            return self.data["night_state"] == "on"
        return None

    @property
    def night_time_begin(self) -> Optional[str]:
        """Return the begin of the night time."""
        return self.data.get("night_beg_time", None)

    @property
    def night_time_end(self) -> Optional[str]:
        """Return the end of the night time."""
        return self.data.get("night_end_time", None)

    @property
    def sensor_state(self) -> Optional[str]:
        """Sensor state."""
        return self.data.get("sensor_state", None)

    @property
    def co2(self) -> Optional[int]:
        """Return co2 value (400...9999ppm)."""
        return self.data.get("co2", None)

    @property
    def co2e(self) -> Optional[int]:
        """Return co2e value (400...9999ppm)."""
        return self.data.get("co2e", None)

    @property
    def humidity(self) -> Optional[float]:
        """Return humidity value (0...100%)."""
        return self.data.get("humidity", None)

    @property
    def pm25(self) -> Optional[float]:
        """Return pm2.5 value (0...999μg/m³)."""
        return self.data.get("pm25", None)

    @property
    def temperature(self) -> Optional[float]:
        """Return temperature value (-10...50°C)."""
        return self.data.get("temperature", None)

    @property
    def tvoc(self) -> Optional[int]:
        """Return tvoc value."""
        return self.data.get("tvoc", None)


class AirQualityMonitor(Device):
    """Xiaomi PM2.5 Air Quality Monitor."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_AIRQUALITYMONITOR_V1,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        elif model is not None:
            self.model = MODEL_AIRQUALITYMONITOR_V1
            _LOGGER.error(
                "Device model %s unsupported. Falling back to %s.", model, self.model
            )
        else:
            # Force autodetection.
            self.model = None

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "USB power: {result.usb_power}\n"
            "Battery: {result.battery}\n"
            "AQI: {result.aqi}\n"
            "Temperature: {result.temperature}\n"
            "Humidity: {result.humidity}\n"
            "CO2: {result.co2}\n"
            "CO2e: {result.co2e}\n"
            "PM2.5: {result.pm25}\n"
            "TVOC: {result.tvoc}\n"
            "Display clock: {result.display_clock}\n",
        )
    )
    def status(self) -> AirQualityMonitorStatus:
        """Return device status."""

        if self.model is None:
            info = self.info()
            self.model = info.model

        properties = AVAILABLE_PROPERTIES[self.model]

        if self.model == MODEL_AIRQUALITYMONITOR_B1:
            values = self.send("get_air_data")
        else:
            values = self.send("get_prop", properties)

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count,
                values_count,
            )

        if (
            self.model == MODEL_AIRQUALITYMONITOR_S1
            or self.model == MODEL_AIRQUALITYMONITOR_B1
        ):
            return AirQualityMonitorStatus(defaultdict(lambda: None, values))
        else:
            return AirQualityMonitorStatus(
                defaultdict(lambda: None, zip(properties, values))
            )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("display_clock", type=bool),
        default_output=format_output(
            lambda led: "Turning on display clock"
            if led
            else "Turning off display clock"
        ),
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
            lambda led: "Turning on auto close" if led else "Turning off auto close"
        ),
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
            lambda led: "Turning on night mode" if led else "Turning off night mode"
        ),
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
            "Setting night time to {begin_hour}:{begin_minute} - {end_hour}:{end_minute}"
        ),
    )
    def set_night_time(
        self, begin_hour: int, begin_minute: int, end_hour: int, end_minute: int
    ):
        """Enable night mode daily at bedtime."""
        begin = begin_hour * 3600 + begin_minute * 60
        end = end_hour * 3600 + end_minute * 60

        if begin < 0 or begin > 86399 or end < 0 or end > 86399:
            AirQualityMonitorException("Begin or/and end time invalid.")

        self.send("set_night_time", [begin, end])
