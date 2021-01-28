from unittest import TestCase

import pytest

from miio import AirPurifierMB4
from miio.airpurifier_miot import AirPurifierMiotException, OperationMode

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": True,
    "mode": 0,
    "aqi": 10,
    "filter_life_remaining": 80,
    "filter_hours_used": 682,
    "buzzer": False,
    "led_brightness_level": 4,
    "child_lock": False,
    "motor_speed": 354,
    "favorite_rpm": 500,
}


class DummyAirPurifierMiot(DummyMiotDevice, AirPurifierMB4):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_favorite_rpm": lambda x: self._set_state("favorite_rpm", x),
            "reset_filter1": lambda x: (
                self._set_state("f1_hour_used", [0]),
                self._set_state("filter1_life", [100]),
            ),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def airpurifier(request):
    request.cls.device = DummyAirPurifierMiot()


@pytest.mark.usefixtures("airpurifier")
class TestAirPurifier(TestCase):
    def test_on(self):
        self.device.off()  # ensure off
        assert self.device.status().is_on is False

        self.device.on()
        assert self.device.status().is_on is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self.device.status().is_on is True

        self.device.off()
        assert self.device.status().is_on is False

    def test_status(self):
        status = self.device.status()
        assert status.is_on is _INITIAL_STATE["power"]
        assert status.aqi == _INITIAL_STATE["aqi"]
        assert status.mode == OperationMode(_INITIAL_STATE["mode"])
        assert status.led_brightness_level == _INITIAL_STATE["led_brightness_level"]
        assert status.buzzer == _INITIAL_STATE["buzzer"]
        assert status.child_lock == _INITIAL_STATE["child_lock"]
        assert status.favorite_rpm == _INITIAL_STATE["favorite_rpm"]
        assert status.filter_life_remaining == _INITIAL_STATE["filter_life_remaining"]
        assert status.filter_hours_used == _INITIAL_STATE["filter_hours_used"]
        assert status.motor_speed == _INITIAL_STATE["motor_speed"]

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Auto)
        assert mode() == OperationMode.Auto

        self.device.set_mode(OperationMode.Silent)
        assert mode() == OperationMode.Silent

        self.device.set_mode(OperationMode.Favorite)
        assert mode() == OperationMode.Favorite

        self.device.set_mode(OperationMode.Fan)
        assert mode() == OperationMode.Fan

    def test_set_favorite_rpm(self):
        def favorite_rpm():
            return self.device.status().favorite_rpm

        self.device.set_favorite_rpm(300)
        assert favorite_rpm() == 300
        self.device.set_favorite_rpm(1000)
        assert favorite_rpm() == 1000
        self.device.set_favorite_rpm(2300)
        assert favorite_rpm() == 2300

        with pytest.raises(AirPurifierMiotException):
            self.device.set_favorite_rpm(301)

        with pytest.raises(AirPurifierMiotException):
            self.device.set_favorite_rpm(290)

        with pytest.raises(AirPurifierMiotException):
            self.device.set_favorite_rpm(2310)

    def test_set_led_brightness_level(self):
        def led_brightness_level():
            return self.device.status().led_brightness_level

        self.device.set_led_brightness_level(0)
        assert led_brightness_level() == 0

        self.device.set_led_brightness_level(4)
        assert led_brightness_level() == 4

        self.device.set_led_brightness_level(8)
        assert led_brightness_level() == 8

        with pytest.raises(AirPurifierMiotException):
            self.device.set_led_brightness_level(-1)

        with pytest.raises(AirPurifierMiotException):
            self.device.set_led_brightness_level(9)

    def test_set_child_lock(self):
        def child_lock():
            return self.device.status().child_lock

        self.device.set_child_lock(True)
        assert child_lock() is True

        self.device.set_child_lock(False)
        assert child_lock() is False
