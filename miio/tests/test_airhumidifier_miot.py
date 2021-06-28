from unittest import TestCase

import pytest

from miio import AirHumidifierMiot
from miio.airhumidifier_miot import (
    AirHumidifierMiotException,
    LedBrightness,
    OperationMode,
    PressedButton,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": True,
    "fault": 0,
    "mode": 0,
    "target_humidity": 60,
    "water_level": 32,
    "dry": True,
    "use_time": 2426773,
    "button_pressed": 1,
    "speed_level": 810,
    "temperature": 21.6,
    "fahrenheit": 70.9,
    "humidity": 62,
    "buzzer": False,
    "led_brightness": 1,
    "child_lock": False,
    "motor_speed": 354,
    "actual_speed": 820,
    "power_time": 4272468,
    "clean_mode": False,
}


class DummyAirHumidifierMiot(DummyMiotDevice, AirHumidifierMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_speed": lambda x: self._set_state("speed_level", x),
            "set_target_humidity": lambda x: self._set_state("target_humidity", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_led_brightness": lambda x: self._set_state("led_brightness", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_dry": lambda x: self._set_state("dry", x),
            "set_clean_mode": lambda x: self._set_state("clean_mode", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def airhumidifier(request):
    request.cls.device = DummyAirHumidifierMiot()


@pytest.mark.usefixtures("airhumidifier")
class TestAirHumidifier(TestCase):
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
        assert status.error == _INITIAL_STATE["fault"]
        assert status.mode == OperationMode(_INITIAL_STATE["mode"])
        assert status.target_humidity == _INITIAL_STATE["target_humidity"]
        assert status.water_level == int(_INITIAL_STATE["water_level"] / 1.25)
        assert status.water_tank_detached == (_INITIAL_STATE["water_level"] == 127)
        assert status.dry == _INITIAL_STATE["dry"]
        assert status.use_time == _INITIAL_STATE["use_time"]
        assert status.button_pressed == PressedButton(_INITIAL_STATE["button_pressed"])
        assert status.motor_speed == _INITIAL_STATE["speed_level"]
        assert status.temperature == _INITIAL_STATE["temperature"]
        assert status.fahrenheit == _INITIAL_STATE["fahrenheit"]
        assert status.humidity == _INITIAL_STATE["humidity"]
        assert status.buzzer == _INITIAL_STATE["buzzer"]
        assert status.led_brightness == LedBrightness(_INITIAL_STATE["led_brightness"])
        assert status.child_lock == _INITIAL_STATE["child_lock"]
        assert status.actual_speed == _INITIAL_STATE["actual_speed"]
        assert status.power_time == _INITIAL_STATE["power_time"]

    def test_set_speed(self):
        def speed_level():
            return self.device.status().motor_speed

        self.device.set_speed(200)
        assert speed_level() == 200
        self.device.set_speed(2000)
        assert speed_level() == 2000

        with pytest.raises(AirHumidifierMiotException):
            self.device.set_speed(199)

        with pytest.raises(AirHumidifierMiotException):
            self.device.set_speed(2001)

    def test_set_target_humidity(self):
        def target_humidity():
            return self.device.status().target_humidity

        self.device.set_target_humidity(30)
        assert target_humidity() == 30
        self.device.set_target_humidity(80)
        assert target_humidity() == 80

        with pytest.raises(AirHumidifierMiotException):
            self.device.set_target_humidity(29)

        with pytest.raises(AirHumidifierMiotException):
            self.device.set_target_humidity(81)

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Auto)
        assert mode() == OperationMode.Auto

        self.device.set_mode(OperationMode.Low)
        assert mode() == OperationMode.Low

        self.device.set_mode(OperationMode.Mid)
        assert mode() == OperationMode.Mid

        self.device.set_mode(OperationMode.High)
        assert mode() == OperationMode.High

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        self.device.set_led_brightness(LedBrightness.Bright)
        assert led_brightness() == LedBrightness.Bright

        self.device.set_led_brightness(LedBrightness.Dim)
        assert led_brightness() == LedBrightness.Dim

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

    def test_set_dry(self):
        def dry():
            return self.device.status().dry

        self.device.set_dry(True)
        assert dry() is True

        self.device.set_dry(False)
        assert dry() is False

    def test_set_clean_mode(self):
        def clean_mode():
            return self.device.status().clean_mode

        self.device.set_clean_mode(True)
        assert clean_mode() is True

        self.device.set_clean_mode(False)
        assert clean_mode() is False
