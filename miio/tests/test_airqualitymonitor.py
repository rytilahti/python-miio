from unittest import TestCase

import pytest

from miio import AirQualityMonitor
from miio.airqualitymonitor import AirQualityMonitorStatus
from .dummies import DummyDevice


class DummyAirQualityMonitor(DummyDevice, AirQualityMonitor):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'aqi': 34,
            'battery': 100,
            'usb_state': 'off',
            'time_state': 'on',
            'night_state': 'on',
            'night_beg_time': 'format unknown',
            'night_end_time': 'format unknown',
            'sensor_state': 'format unknown',
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_time_state': lambda x: self._set_state("time_state", x),
            'set_night_state': lambda x: self._set_state("night_state", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def airqualitymonitor(request):
    request.cls.device = DummyAirQualityMonitor()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("airqualitymonitor")
class TestAirQualityMonitor(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_on(self):
        self.device.off()  # ensure off
        assert self.is_on() is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self.is_on() is True

        self.device.off()
        assert self.is_on() is False

    def test_status(self):
        self.device._reset_state()

        assert repr(self.state()) == repr(AirQualityMonitorStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().aqi == self.device.start_state["aqi"]
        assert self.state().battery == self.device.start_state["battery"]
        assert self.state().usb_power is (self.device.start_state["usb_state"] == 'on')
        assert self.state().display_clock is (self.device.start_state["time_state"] == 'on')
        assert self.state().night_mode is (self.device.start_state["night_state"] == 'on')
