from unittest import TestCase

import pytest

from miio.tests.dummies import DummyDevice

from .fan import MODEL_FAN_P5, FanP5, FanStatusP5, OperationMode


class DummyFanP5(DummyDevice, FanP5):
    def __init__(self, *args, **kwargs):
        self._model = MODEL_FAN_P5
        self.state = {
            "power": True,
            "mode": "normal",
            "speed": 35,
            "roll_enable": False,
            "roll_angle": 140,
            "time_off": 0,
            "light": True,
            "beep_sound": False,
            "child_lock": False,
        }

        self.return_values = {
            "get_prop": self._get_state,
            "s_power": lambda x: self._set_state("power", x),
            "s_mode": lambda x: self._set_state("mode", x),
            "s_speed": lambda x: self._set_state("speed", x),
            "s_roll": lambda x: self._set_state("roll_enable", x),
            "s_angle": lambda x: self._set_state("roll_angle", x),
            "s_t_off": lambda x: self._set_state("time_off", x),
            "s_light": lambda x: self._set_state("light", x),
            "s_sound": lambda x: self._set_state("beep_sound", x),
            "s_lock": lambda x: self._set_state("child_lock", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def fanp5(request):
    request.cls.device = DummyFanP5()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("fanp5")
class TestFanP5(TestCase):
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

        assert repr(self.state()) == repr(FanStatusP5(self.device.start_state))

        assert self.is_on() is True
        assert self.state().mode == OperationMode(self.device.start_state["mode"])
        assert self.state().speed == self.device.start_state["speed"]
        assert self.state().oscillate is self.device.start_state["roll_enable"]
        assert self.state().angle == self.device.start_state["roll_angle"]
        assert self.state().delay_off_countdown == self.device.start_state["time_off"]
        assert self.state().led is self.device.start_state["light"]
        assert self.state().buzzer is self.device.start_state["beep_sound"]
        assert self.state().child_lock is self.device.start_state["child_lock"]

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

        with pytest.raises(ValueError):
            self.device.set_speed(-1)

        with pytest.raises(ValueError):
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

        with pytest.raises(ValueError):
            self.device.set_angle(-1)

        with pytest.raises(ValueError):
            self.device.set_angle(1)

        with pytest.raises(ValueError):
            self.device.set_angle(31)

        with pytest.raises(ValueError):
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

        with pytest.raises(ValueError):
            self.device.delay_off(-1)
