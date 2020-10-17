from unittest import TestCase

import pytest

from miio import FanMiot
from miio.fan_miot import (
    MODEL_FAN_P9,
    FanException,
    FanMiotDeviceAdapter,
    OperationMode,
    PropertyAdapter,
)

from .dummies import DummyMiotV2Device


class TestFanMiotDeviceAdapter(TestCase):
    def test_check_validation(self):
        adapter = FanMiotDeviceAdapter(
            "urn:miot-spec-v2:device:fan:0000A005:dmaker-p11:1.json",
            speed=PropertyAdapter("fan", "fan-level"),
            off_delay=PropertyAdapter("off-delay-time", "off-delay-time"),
            alarm=PropertyAdapter("alarm", "alarm"),
            brightness=PropertyAdapter("indicator-light", "on"),
            motor_control=PropertyAdapter("motor-controller", "motor-control"),
        )
        adapter.check_validation()


class DummyFanMiot(DummyMiotV2Device, FanMiot):
    def __init__(self, *args, **kwargs):
        self.model = MODEL_FAN_P9
        self.adapter = self.get_adapter()
        self.spec = self.adapter.spec
        self.state = {
            "fan.on": True,
            "fan.mode": 0,
            "fan.speed-level": 35,
            "fan.horizontal-swing": False,
            "fan.horizontal-angle": 140,
            "fan.off-delay-time": 0,
            "fan.brightness": True,
            "fan.alarm": False,
            "physical-controls-locked": False,
        }
        self.return_values = {
            "get_prop": self._get_state,
            "fan.on": lambda x: self._set_state("power", x),
            "fan.mode": lambda x: self._set_state("mode", x),
            "fan.speed-level": lambda x: self._set_state("fan_speed", x),
            "fan.horizontal-swing": lambda x: self._set_state("swing_mode", x),
            "fan.horizontal-angle": lambda x: self._set_state("swing_mode_angle", x),
            "fan.off-delay-time": lambda x: self._set_state("power_off_time", x),
            "fan.brightness": lambda x: self._set_state("light", x),
            "fan.alarm": lambda x: self._set_state("buzzer", x),
            "physical-controls-locked": lambda x: self._set_state("child_lock", x),
            "motor-control": lambda x: True,
        }
        super().__init__(args, kwargs)

    def get_adapter(self):
        return FanMiotDeviceAdapter(
            "urn:miot-spec-v2:device:fan:0000A005:dmaker-p9:1.json"
        )


@pytest.fixture(scope="class")
def fanmiot(request):
    request.cls.device = DummyFanMiot()


@pytest.mark.usefixtures("fanmiot")
class TestFanMiot(TestCase):
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

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationMode.Normal)
        assert mode() == OperationMode.Normal

        self.device.set_mode(OperationMode.Nature)
        assert mode() == OperationMode.Nature

    def test_set_speed(self):
        def speed():
            return self.device.status().speed

        self.device.set_speed(0)
        assert speed() == 0
        self.device.set_speed(1)
        assert speed() == 1
        self.device.set_speed(100)
        assert speed() == 100

        with pytest.raises(FanException):
            self.device.set_speed(-1)

        with pytest.raises(FanException):
            self.device.set_speed(101)

    def test_set_angle(self):
        def angle():
            return self.device.status().angle

        self.device.set_angle(30)
        assert angle() == 30
        self.device.set_angle(60)
        assert angle() == 60
        self.device.set_angle(90)
        assert angle() == 90
        self.device.set_angle(120)
        assert angle() == 120
        self.device.set_angle(140)
        assert angle() == 140

        with pytest.raises(FanException):
            self.device.set_angle(-1)

        with pytest.raises(FanException):
            self.device.set_angle(1)

        with pytest.raises(FanException):
            self.device.set_angle(31)

        with pytest.raises(FanException):
            self.device.set_angle(141)

    def test_set_oscillate(self):
        def oscillate():
            return self.device.status().oscillate

        self.device.set_oscillate(True)
        assert oscillate() is True

        self.device.set_oscillate(False)
        assert oscillate() is False

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

    def test_set_child_lock(self):
        def child_lock():
            return self.device.status().child_lock

        self.device.set_child_lock(True)
        assert child_lock() is True

        self.device.set_child_lock(False)
        assert child_lock() is False

    def test_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        self.device.delay_off(100)
        assert delay_off_countdown() == 100
        self.device.delay_off(200)
        assert delay_off_countdown() == 200
        self.device.delay_off(0)
        assert delay_off_countdown() == 0

        with pytest.raises(FanException):
            self.device.delay_off(-1)
