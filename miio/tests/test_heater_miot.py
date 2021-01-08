from unittest import TestCase

import pytest

from miio import HeaterMiot
from miio.heater_miot import HeaterMiotException, LedBrightness

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": True,
    "temperature": 21.6,
    "target_temperature": 23,
    "buzzer": False,
    "led_brightness": 1,
    "child_lock": False,
    "countdown_time": 0,
}


class DummyHeaterMiot(DummyMiotDevice, HeaterMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_led_brightness": lambda x: self._set_state("led_brightness", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_delay_off": lambda x: self._set_state("countdown_time", x),
            "set_target_temperature": lambda x: self._set_state(
                "target_temperature", x
            ),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="class")
def heater(request):
    request.cls.device = DummyHeaterMiot()


@pytest.mark.usefixtures("heater")
class TestHeater(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def test_on(self):
        self.device.off()
        assert self.is_on() is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()
        assert self.is_on() is True

        self.device.off()
        assert self.is_on() is False

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightness.On)
        assert led_brightness() == LedBrightness.On

        self.device.set_led_brightness(LedBrightness.Off)
        assert led_brightness() == LedBrightness.Off

    def test_set_buzzer(self):
        def buzzer():
            return self.device.status().buzzer

        self.device.set_buzzer(True)
        assert buzzer() is True

        self.device.set_buzzer(False)
        assert buzzer() is False

    def test_set_child_lock(self):
        def child_lock():
            return self.device.status().child_lock

        self.device.set_child_lock(True)
        assert child_lock() is True

        self.device.set_child_lock(False)
        assert child_lock() is False

    def test_set_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        self.device.set_delay_off(0)
        assert delay_off_countdown() == 0
        self.device.set_delay_off(9 * 3600)
        assert delay_off_countdown() == 9
        self.device.set_delay_off(12 * 3600)
        assert delay_off_countdown() == 12
        self.device.set_delay_off(9 * 3600 + 1)
        assert delay_off_countdown() == 9

        with pytest.raises(HeaterMiotException):
            self.device.set_delay_off(-1)

        with pytest.raises(HeaterMiotException):
            self.device.set_delay_off(13 * 3600)

    def test_set_target_temperature(self):
        def target_temperature():
            return self.device.status().target_temperature

        self.device.set_target_temperature(18)
        assert target_temperature() == 18

        self.device.set_target_temperature(23)
        assert target_temperature() == 23

        self.device.set_target_temperature(28)
        assert target_temperature() == 28

        with pytest.raises(HeaterMiotException):
            self.device.set_target_temperature(17)

        with pytest.raises(HeaterMiotException):
            self.device.set_target_temperature(29)
