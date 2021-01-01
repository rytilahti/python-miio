from unittest import TestCase

import pytest

from miio import AirQualityMonitorCGDN1
from miio.airqualitymonitor_miot import (
    ChargingStateCGDN1,
    DeviceOffCGDN1,
    DisplayTemeratureUnitCGDN1,
    MonitoringFrequencyCGDN1,
    ScreenOffCGDN1,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "humidity": 34,
    "pm25": 10,
    "pm10": 15,
    "temperature": 18.599999,
    "co2": 620,
    "battery": 20,
    "charging_state": 2,
    "voltage": 26,
    "start_time": 0,
    "end_time": 0,
    "monitoring_frequency": 1,
    "screen_off": 15,
    "device_off": 30,
    "temperature_unit": "c",
}


class DummyAirQualityMonitorCGDN1(DummyMiotDevice, AirQualityMonitorCGDN1):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_monitoring_frequency": lambda x: self._set_state(
                "monitoring_frequency", x
            ),
            "set_device_off_duration": lambda x: self._set_state("device_off", x),
            "set_screen_off_duration": lambda x: self._set_state("screen_off", x),
            "set_display_temerature_unit": lambda x: self._set_state(
                "temperature_unit", x
            ),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def airqualitymonitorcgdn1(request):
    request.cls.device = DummyAirQualityMonitorCGDN1()


@pytest.mark.usefixtures("airqualitymonitorcgdn1")
class TestAirQualityMonitor(TestCase):
    def test_status(self):
        status = self.device.status()
        assert status.humidity is _INITIAL_STATE["humidity"]
        assert status.pm25 is _INITIAL_STATE["pm25"]
        assert status.pm10 is _INITIAL_STATE["pm10"]
        assert status.temperature is _INITIAL_STATE["temperature"]
        assert status.co2 is _INITIAL_STATE["co2"]
        assert status.battery is _INITIAL_STATE["battery"]
        assert status.charging_state is ChargingStateCGDN1(
            _INITIAL_STATE["charging_state"]
        )
        assert status.monitoring_frequency is MonitoringFrequencyCGDN1(
            _INITIAL_STATE["monitoring_frequency"]
        )
        assert status.screen_off is ScreenOffCGDN1(_INITIAL_STATE["screen_off"])
        assert status.display_temperature_unit is DisplayTemeratureUnitCGDN1(
            _INITIAL_STATE["temperature_unit"]
        )

    def test_set_monitoring_frequency(self):
        def monitoring_frequency():
            return self.device.status().monitoring_frequency

        self.device.set_monitoring_frequency(MonitoringFrequencyCGDN1.Every1Second)
        assert monitoring_frequency() == MonitoringFrequencyCGDN1.Every1Second

        self.device.set_monitoring_frequency(MonitoringFrequencyCGDN1.Every1Minute)
        assert monitoring_frequency() == MonitoringFrequencyCGDN1.Every1Minute

        self.device.set_monitoring_frequency(MonitoringFrequencyCGDN1.Every5Minutes)
        assert monitoring_frequency() == MonitoringFrequencyCGDN1.Every5Minutes

        self.device.set_monitoring_frequency(MonitoringFrequencyCGDN1.Every10Minutes)
        assert monitoring_frequency() == MonitoringFrequencyCGDN1.Every10Minutes

        self.device.set_monitoring_frequency(MonitoringFrequencyCGDN1.NotSet)
        assert monitoring_frequency() == MonitoringFrequencyCGDN1.NotSet

    def test_set_device_off_duration(self):
        def device_off_duration():
            return self.device.status().device_off

        self.device.set_device_off_duration(DeviceOffCGDN1.After15Minutes)
        assert device_off_duration() == DeviceOffCGDN1.After15Minutes

        self.device.set_device_off_duration(DeviceOffCGDN1.After30Minutes)
        assert device_off_duration() == DeviceOffCGDN1.After30Minutes

        self.device.set_device_off_duration(DeviceOffCGDN1.After1Hour)
        assert device_off_duration() == DeviceOffCGDN1.After1Hour

        self.device.set_device_off_duration(DeviceOffCGDN1.Never)
        assert device_off_duration() == DeviceOffCGDN1.Never

    def test_set_screen_off_duration(self):
        def screen_off_duration():
            return self.device.status().screen_off

        self.device.set_screen_off_duration(ScreenOffCGDN1.After15Seconds)
        assert screen_off_duration() == ScreenOffCGDN1.After15Seconds

        self.device.set_screen_off_duration(ScreenOffCGDN1.After30Seconds)
        assert screen_off_duration() == ScreenOffCGDN1.After30Seconds

        self.device.set_screen_off_duration(ScreenOffCGDN1.After1Minute)
        assert screen_off_duration() == ScreenOffCGDN1.After1Minute

        self.device.set_screen_off_duration(ScreenOffCGDN1.After5Minutes)
        assert screen_off_duration() == ScreenOffCGDN1.After5Minutes

        self.device.set_screen_off_duration(ScreenOffCGDN1.Never)
        assert screen_off_duration() == ScreenOffCGDN1.Never

    def test_set_display_temerature_unit(self):
        def display_temerature_unit():
            return self.device.status().display_temperature_unit

        self.device.set_display_temerature_unit(DisplayTemeratureUnitCGDN1.Celcius)
        assert display_temerature_unit() == DisplayTemeratureUnitCGDN1.Celcius

        self.device.set_display_temerature_unit(DisplayTemeratureUnitCGDN1.Fahrenheit)
        assert display_temerature_unit() == DisplayTemeratureUnitCGDN1.Fahrenheit
