from unittest import TestCase

import pytest

from miio.tests.dummies import DummyMiotDevice

from . import FanZA5
from .zhimi_miot import MODEL_FAN_ZA5, OperationMode, OperationModeFanZA5


class DummyFanZA5(DummyMiotDevice, FanZA5):
    def __init__(self, *args, **kwargs):
        self._model = MODEL_FAN_ZA5
        self.state = {
            "anion": True,
            "buzzer": False,
            "child_lock": False,
            "fan_speed": 42,
            "light": 44,
            "mode": OperationModeFanZA5.Normal.value,
            "power": True,
            "power_off_time": 0,
            "swing_mode": True,
            "swing_mode_angle": 60,
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def fanza5(request):
    request.cls.device = DummyFanZA5()


@pytest.mark.usefixtures("fanza5")
class TestFanZA5(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def is_ionizer_enabled(self):
        return self.device.status().is_ionizer_enabled

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

    def test_ionizer(self):
        def ionizer():
            return self.device.status().ionizer

        self.device.set_ionizer(True)
        assert ionizer() is True

        self.device.set_ionizer(False)
        assert ionizer() is False

    def test_set_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_mode(OperationModeFanZA5.Normal)
        assert mode() == OperationMode.Normal

        self.device.set_mode(OperationModeFanZA5.Nature)
        assert mode() == OperationMode.Nature

    def test_set_speed(self):
        def speed():
            return self.device.status().speed

        for s in range(1, 101):
            self.device.set_speed(s)
            assert speed() == s

        for s in (-1, 0, 101):
            with pytest.raises(ValueError):
                self.device.set_speed(s)

    def test_fan_speed_deprecation(self):
        with pytest.deprecated_call():
            self.device.status().fan_speed

    def test_set_angle(self):
        def angle():
            return self.device.status().angle

        for a in (30, 60, 90, 120):
            self.device.set_angle(a)
            assert angle() == a

        for a in (0, 45, 140):
            with pytest.raises(ValueError):
                self.device.set_angle(a)

    def test_set_oscillate(self):
        def oscillate():
            return self.device.status().oscillate

        self.device.set_oscillate(True)
        assert oscillate() is True

        self.device.set_oscillate(False)
        assert oscillate() is False

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

    def test_set_led_brightness(self):
        def led_brightness():
            return self.device.status().led_brightness

        for brightness in range(101):
            self.device.set_led_brightness(brightness)
            assert led_brightness() == brightness

        for brightness in (-1, 101):
            with pytest.raises(ValueError):
                self.device.set_led_brightness(brightness)

    def test_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        for delay in (0, 1, 36000):
            self.device.delay_off(delay)
            assert delay_off_countdown() == delay

        for delay in (-1, 36001):
            with pytest.raises(ValueError):
                self.device.delay_off(delay)
