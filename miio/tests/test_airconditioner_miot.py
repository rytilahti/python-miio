from unittest import TestCase

import pytest

from miio import AirConditionerMiot
from miio.airconditioner_miot import (
    AirConditionerMiotException,
    CleaningStatus,
    FanSpeed,
    OperationMode,
    TimerStatus,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": False,
    "mode": OperationMode.Cool,
    "target_temperature": 24,
    "eco": True,
    "heater": True,
    "dryer": False,
    "sleep_mode": False,
    "fan_speed": FanSpeed.Level7,
    "vertical_swing": True,
    "temperature": 27.5,
    "buzzer": True,
    "led": False,
    "electricity": 0.0,
    "clean": "0,100,1,1",
    "running_duration": 100.4,
    "fan_speed_percent": 90,
    "timer": "0,0,0,0",
}


class DummyAirConditionerMiot(DummyMiotDevice, AirConditionerMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_target_temperature": lambda x: self._set_state(
                "target_temperature", x
            ),
            "set_eco": lambda x: self._set_state("eco", x),
            "set_heater": lambda x: self._set_state("heater", x),
            "set_dryer": lambda x: self._set_state("dryer", x),
            "set_sleep_mode": lambda x: self._set_state("sleep_mode", x),
            "set_fan_speed": lambda x: self._set_state("fan_speed", x),
            "set_vertical_swing": lambda x: self._set_state("vertical_swing", x),
            "set_temperature": lambda x: self._set_state("temperature", x),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_led": lambda x: self._set_state("led", x),
            "set_clean": lambda x: self._set_state("clean", x),
            "set_fan_speed_percent": lambda x: self._set_state("fan_speed_percent", x),
            "set_timer": lambda x, y: self._set_state("timer", x, y),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def airconditionermiot(request):
    request.cls.device = DummyAirConditionerMiot()


@pytest.mark.usefixtures("airconditionermiot")
class TestAirConditioner(TestCase):
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
        assert status.is_on == _INITIAL_STATE["power"]
        assert status.mode == OperationMode(_INITIAL_STATE["mode"])
        assert status.target_temperature == _INITIAL_STATE["target_temperature"]
        assert status.eco == _INITIAL_STATE["eco"]
        assert status.heater == _INITIAL_STATE["heater"]
        assert status.dryer == _INITIAL_STATE["dryer"]
        assert status.sleep_mode == _INITIAL_STATE["sleep_mode"]
        assert status.fan_speed == FanSpeed(_INITIAL_STATE["fan_speed"])
        assert status.vertical_swing == _INITIAL_STATE["vertical_swing"]
        assert status.temperature == _INITIAL_STATE["temperature"]
        assert status.buzzer == _INITIAL_STATE["buzzer"]
        assert status.led == _INITIAL_STATE["led"]
        assert repr(status.clean) == repr(CleaningStatus(_INITIAL_STATE["clean"]))
        assert status.fan_speed_percent == _INITIAL_STATE["fan_speed_percent"]
        assert repr(status.timer) == repr(TimerStatus(_INITIAL_STATE["timer"]))

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Cool)
        assert mode() == OperationMode.Cool

        self.device.set_mode(OperationMode.Dry)
        assert mode() == OperationMode.Dry

        self.device.set_mode(OperationMode.Fan)
        assert mode() == OperationMode.Fan

        self.device.set_mode(OperationMode.Heat)
        assert mode() == OperationMode.Heat

    def test_set_target_temperature(self):
        def target_temperature():
            return self.device.status().target_temperature

        self.device.set_target_temperature(16.0)
        assert target_temperature() == 16.0
        self.device.set_target_temperature(31.0)
        assert target_temperature() == 31.0

        with pytest.raises(AirConditionerMiotException):
            self.device.set_target_temperature(15.5)

        with pytest.raises(AirConditionerMiotException):
            self.device.set_target_temperature(24.6)

        with pytest.raises(AirConditionerMiotException):
            self.device.set_target_temperature(31.5)

    def test_set_eco(self):
        def eco():
            return self.device.status().eco

        self.device.set_eco(True)
        assert eco() is True

        self.device.set_eco(False)
        assert eco() is False

    def test_set_heater(self):
        def heater():
            return self.device.status().heater

        self.device.set_heater(True)
        assert heater() is True

        self.device.set_heater(False)
        assert heater() is False

    def test_set_dryer(self):
        def dryer():
            return self.device.status().dryer

        self.device.set_dryer(True)
        assert dryer() is True

        self.device.set_dryer(False)
        assert dryer() is False

    def test_set_sleep_mode(self):
        def sleep_mode():
            return self.device.status().sleep_mode

        self.device.set_sleep_mode(True)
        assert sleep_mode() is True

        self.device.set_sleep_mode(False)
        assert sleep_mode() is False

    def test_set_fan_speed(self):
        def fan_speed():
            return self.device.status().fan_speed

        self.device.set_fan_speed(FanSpeed.Auto)
        assert fan_speed() == FanSpeed.Auto

        self.device.set_fan_speed(FanSpeed.Level1)
        assert fan_speed() == FanSpeed.Level1

        self.device.set_fan_speed(FanSpeed.Level2)
        assert fan_speed() == FanSpeed.Level2

        self.device.set_fan_speed(FanSpeed.Level3)
        assert fan_speed() == FanSpeed.Level3

        self.device.set_fan_speed(FanSpeed.Level4)
        assert fan_speed() == FanSpeed.Level4

        self.device.set_fan_speed(FanSpeed.Level5)
        assert fan_speed() == FanSpeed.Level5

        self.device.set_fan_speed(FanSpeed.Level6)
        assert fan_speed() == FanSpeed.Level6

        self.device.set_fan_speed(FanSpeed.Level7)
        assert fan_speed() == FanSpeed.Level7

    def test_set_vertical_swing(self):
        def vertical_swing():
            return self.device.status().vertical_swing

        self.device.set_vertical_swing(True)
        assert vertical_swing() is True

        self.device.set_vertical_swing(False)
        assert vertical_swing() is False

    def test_set_led(self):
        def led():
            return self.device.status().led

        self.device.set_led(True)
        assert led() is True

        self.device.set_led(False)
        assert led() is False

    def test_set_buzzer(self):
        def buzzer():
            return self.device.status().buzzer

        self.device.set_buzzer(True)
        assert buzzer() is True

        self.device.set_buzzer(False)
        assert buzzer() is False

    def test_set_fan_speed_percent(self):
        def fan_speed_percent():
            return self.device.status().fan_speed_percent

        self.device.set_fan_speed_percent(1)
        assert fan_speed_percent() == 1
        self.device.set_fan_speed_percent(101)
        assert fan_speed_percent() == 101

        with pytest.raises(AirConditionerMiotException):
            self.device.set_fan_speed_percent(102)

        with pytest.raises(AirConditionerMiotException):
            self.device.set_fan_speed_percent(0)

    def test_set_timer(self):
        def timer():
            return self.device.status().data["timer"]

        self.device.set_timer(60, True)
        assert timer() == "1,60,1"

        self.device.set_timer(120, False)
        assert timer() == "1,120,0"

    def test_set_clean(self):
        def clean():
            return self.device.status().data["clean"]

        self.device.set_clean(True)
        assert clean() == "1"

        self.device.set_clean(False)
        assert clean() == "0"
