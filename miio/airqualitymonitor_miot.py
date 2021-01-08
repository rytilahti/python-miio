import enum
import logging

import click

from .click_common import command, format_output
from .exceptions import DeviceException
from .miot_device import MiotDevice

_LOGGER = logging.getLogger(__name__)

MODEL_AIRQUALITYMONITOR_CGDN1 = "cgllc.airm.cgdn1"

_MAPPING_CGDN1 = {
    # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-monitor:0000A008:cgllc-cgdn1:1
    # Environment
    "humidity": {"siid": 3, "piid": 1},  # [0, 100] step 1
    "pm25": {"siid": 3, "piid": 4},  # [0, 1000] step 1
    "pm10": {"siid": 3, "piid": 5},  # [0, 1000] step 1
    "temperature": {"siid": 3, "piid": 7},  # [-30, 100] step 0.00001
    "co2": {"siid": 3, "piid": 8},  # [0, 9999] step 1
    # Battery
    "battery": {"siid": 4, "piid": 1},  # [0, 100] step 1
    "charging_state": {
        "siid": 4,
        "piid": 2,
    },  # 1 - Charging, 2 - Not charging, 3 - Not chargeable
    "voltage": {"siid": 4, "piid": 3},  # [0, 65535] step 1
    # Settings
    "start_time": {"siid": 9, "piid": 2},  # [0, 2147483647] step 1
    "end_time": {"siid": 9, "piid": 3},  # [0, 2147483647] step 1
    "monitoring_frequency": {
        "siid": 9,
        "piid": 4,
    },  # 1, 60, 300, 600, 0; device accepts [0..600]
    "screen_off": {
        "siid": 9,
        "piid": 5,
    },  # 15, 30, 60, 300, 0; device accepts [0..300], 0 means never
    "device_off": {
        "siid": 9,
        "piid": 6,
    },  # 15, 30, 60, 0; device accepts [0..60], 0 means never
    "temperature_unit": {"siid": 9, "piid": 7},
}


class AirQualityMonitorMiotException(DeviceException):
    pass


class ChargingState(enum.Enum):
    Unplugged = 0  # Not mentioned in the spec
    Charging = 1
    NotCharging = 2
    NotChargable = 3


class MonitoringFrequencyCGDN1(enum.Enum):  # Official spec options
    Every1Second = 1
    Every1Minute = 60
    Every5Minutes = 300
    Every10Minutes = 600
    NotSet = 0


class ScreenOffCGDN1(enum.Enum):  # Official spec options
    After15Seconds = 15
    After30Seconds = 30
    After1Minute = 60
    After5Minutes = 300
    Never = 0


class DeviceOffCGDN1(enum.Enum):  # Official spec options
    After15Minutes = 15
    After30Minutes = 30
    After1Hour = 60
    Never = 0


class DisplayTemeratureUnitCGDN1(enum.Enum):
    Celcius = "c"
    Fahrenheit = "f"


class AirQualityMonitorCGDN1Status:
    """
    Container of air quality monitor CGDN1 status.

    {
      'humidity': 34,
      'pm25': 18,
      'pm10': 21,
      'temperature': 22.8,
      'co2': 468,
      'battery': 37,
      'charging_state': 0,
      'voltage': 3564,
      'start_time': 0,
      'end_time': 0,
      'monitoring_frequency': 1,
      'screen_off': 300,
      'device_off': 60,
      'temperature_unit': 'c'
    }

    """

    def __init__(self, data):
        self.data = data
        self._monitoring_frequency_options = MonitoringFrequencyCGDN1
        self._screen_off_options = ScreenOffCGDN1
        self._device_off_options = DeviceOffCGDN1

    @property
    def humidity(self) -> int:
        """Return humidity value (0...100%)."""
        return self.data["humidity"]

    @property
    def pm25(self) -> int:
        """Return PM 2.5 value (0...1000ppm)."""
        return self.data["pm25"]

    @property
    def pm10(self) -> int:
        """Return PM 10 value (0...1000ppm)."""
        return self.data["pm10"]

    @property
    def temperature(self) -> float:
        """Return temperature value (-30...100°C)."""
        return self.data["temperature"]

    @property
    def co2(self) -> int:
        """Return co2 value (0...9999ppm)."""
        return self.data["co2"]

    @property
    def battery(self) -> int:
        """Return battery level (0...100%)."""
        return self.data["battery"]

    @property
    def charging_state(self) -> ChargingState:
        """Return charging state."""
        return ChargingState(self.data["charging_state"])

    @property
    def monitoring_frequency(self) -> int:
        """Return monitoring frequency time (0..600 s)."""
        return self.data["monitoring_frequency"]

    @property
    def screen_off(self) -> int:
        """Return screen off time (0..300 s)."""
        return self.data["screen_off"]

    @property
    def device_off(self) -> int:
        """Return device off time (0..60 min)."""
        return self.data["device_off"]

    @property
    def display_temperature_unit(self):
        """Return display temperature unit."""
        return DisplayTemeratureUnitCGDN1(self.data["temperature_unit"])

    def __repr__(self) -> str:
        s = (
            "<AirQualityMonitorCGDN1Status humidity=%s, "
            "pm25=%s, "
            "pm10=%s, "
            "temperature=%s, "
            "co2=%s, "
            "battery=%s, "
            "charging_state=%s"
            "monitoring_frequency=%s"
            "screen_off=%s"
            "device_off=%s"
            "display_temerature_unit=%s>"
            % (
                self.humidity,
                self.pm25,
                self.pm10,
                self.temperature,
                self.co2,
                self.battery,
                self.charging_state,
                self.monitoring_frequency,
                self.screen_off,
                self.device_off,
                self.display_temperature_unit,
            )
        )
        return s


class AirQualityMonitorCGDN1(MiotDevice):
    """Qingping Air Monitor Lite."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(_MAPPING_CGDN1, ip, token, start_id, debug, lazy_discover)

    @command(
        default_output=format_output(
            "",
            "Humidity: {result.humidity} %\n"
            "PM 2.5: {result.pm25} μg/m³\n"
            "PM 10: {result.pm10} μg/m³\n"
            "Temperature: {result.temperature} °C\n"
            "CO₂: {result.co2} μg/m³\n"
            "Battery: {result.battery} %\n"
            "Charging state: {result.charging_state.name}\n"
            "Monitoring frequency: {result.monitoring_frequency} s\n"
            "Screen off: {result.screen_off} s\n"
            "Device off: {result.device_off} min\n"
            "Display temperature unit: {result.display_temperature_unit.name}\n",
        )
    )
    def status(self) -> AirQualityMonitorCGDN1Status:
        """Retrieve properties."""

        return AirQualityMonitorCGDN1Status(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("duration", type=int),
        default_output=format_output("Setting monitoring frequency to {duration} s"),
    )
    def set_monitoring_frequency_duration(self, duration):
        """Set monitoring frequency."""
        if duration < 0 or duration > 600:
            raise AirQualityMonitorMiotException(
                "Invalid duration: %s. Must be between 0 and 600" % duration
            )
        return self.set_property("monitoring_frequency", duration)

    @command(
        click.argument("duration", type=int),
        default_output=format_output("Setting device off duration to {duration} min"),
    )
    def set_device_off_duration(self, duration):
        """Set device off duration."""
        if duration < 0 or duration > 60:
            raise AirQualityMonitorMiotException(
                "Invalid duration: %s. Must be between 0 and 60" % duration
            )
        return self.set_property("device_off", duration)

    @command(
        click.argument("duration", type=int),
        default_output=format_output("Setting screen off duration to {duration} s"),
    )
    def set_screen_off_duration(self, duration):
        """Set screen off duration."""
        if duration < 0 or duration > 300:
            raise AirQualityMonitorMiotException(
                "Invalid duration: %s. Must be between 0 and 300" % duration
            )
        return self.set_property("screen_off", duration)

    @command(
        click.argument(
            "unit",
            type=click.Choice(DisplayTemeratureUnitCGDN1.__members__),
            callback=lambda c, p, v: getattr(DisplayTemeratureUnitCGDN1, v),
        ),
        default_output=format_output("Setting display temperature unit to {unit.name}"),
    )
    def set_display_temerature_unit(self, unit: DisplayTemeratureUnitCGDN1):
        """Set display temerature unit."""
        return self.set_property("temperature_unit", unit.value)