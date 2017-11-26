from unittest import TestCase
from miio import Plug
from .dummies import DummyDevice
import pytest


class DummyAirPurifier(DummyDevice, Plug):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'aqi': 10,
            'average_aqi': 8,
            'humidity': 62,
            'temp_dec': 186,
            'mode': 'auto',
            'favorite_level': 10,
            'filter1_life': 80,
            'f1_hour_used': 682,
            'use_time': 2457000,
            'motor1_speed': 354,
            'purify_volume': 25262,
            'f1_hour': 3500,
            'led': 'off',
            'led_b': 2,
            'bright': None,
            'buzzer': 'off',
            'child_lock': 'off'
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_mode': lambda x: self._set_state("mode", x),
            'set_led': lambda x: self._set_state("led", x),
            'set_buzzer': lambda x: self._set_state("buzzer", x),
            'set_child_lock': lambda x: self._set_state("child_lock", x),
            'set_level_favorite':
                lambda x: self._set_state("favorite_level", x),
            'set_led_b': lambda x: self._set_state("led_b", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def airpurifier(request):
    request.cls.device = DummyAirPurifier()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("airpurifier")
class TestAirPurifier(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_on(self):
        self.device.off()  # ensure off

        start_state = self.is_on()
        assert start_state is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()  # ensure on

        assert self.is_on() is True
        self.device.off()
        assert self.is_on() is False

    def test_status(self):
        self.device._reset_state()

        assert self.is_on() is True
        assert self.state().temperature == \
               self.device.start_state["temp_dec"] / 10.0
