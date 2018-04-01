from unittest import TestCase

import pytest

from miio import Ceil
from miio.ceil import CeilStatus, CeilException
from .dummies import DummyDevice


class DummyCeil(DummyDevice, Ceil):
    def __init__(self, *args, **kwargs):
        self.state = {'power': 'on',
                      'bright': 50,
                      'snm': 4,
                      'dv': 0,
                      'cctsw': [[0, 3], [0, 2], [0, 1]],
                      'bl': 1,
                      'mb': 1,
                      'ac': 1,
                      'mssw': 1,
                      'cct': 99
                      }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_bright': lambda x: self._set_state("bright", x),
            'apply_fixed_scene': lambda x: self._set_state("snm", x),
            'delay_off': lambda x: self._set_state("dv", x),
            'enable_bl': lambda x: self._set_state("bl", x),
            'enable_ac': lambda x: self._set_state("ac", x),
            'set_cct': lambda x: self._set_state("cct", x),
            'set_bricct': lambda x: (
                self._set_state('bright', [x[0]]),
                self._set_state('cct', [x[1]])
            ),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def ceil(request):
    request.cls.device = DummyCeil()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("ceil")
class TestCeil(TestCase):
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

        assert repr(self.state()) == repr(CeilStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().brightness == self.device.start_state["bright"]
        assert self.state().color_temperature == self.device.start_state["cct"]
        assert self.state().scene == self.device.start_state["snm"]
        assert self.state().delay_off_countdown == self.device.start_state["dv"]
        assert self.state().smart_night_light is (self.device.start_state["bl"] == 1)
        assert self.state().automatic_color_temperature is (self.device.start_state["ac"] == 1)

    def test_set_brightness(self):
        def brightness():
            return self.device.status().brightness

        self.device.set_brightness(10)
        assert brightness() == 10
        self.device.set_brightness(20)
        assert brightness() == 20

        with pytest.raises(CeilException):
            self.device.set_brightness(-1)

        with pytest.raises(CeilException):
            self.device.set_brightness(101)

    def test_set_color_temperature(self):
        def color_temperature():
            return self.device.status().color_temperature

        self.device.set_color_temperature(30)
        assert color_temperature() == 30
        self.device.set_color_temperature(20)
        assert color_temperature() == 20

        with pytest.raises(CeilException):
            self.device.set_color_temperature(-1)

        with pytest.raises(CeilException):
            self.device.set_color_temperature(101)

    def test_set_brightness_and_color_temperature(self):
        def color_temperature():
            return self.device.status().color_temperature

        def brightness():
            return self.device.status().brightness

        self.device.set_brightness_and_color_temperature(20, 21)
        assert brightness() == 20
        assert color_temperature() == 21
        self.device.set_brightness_and_color_temperature(31, 30)
        assert brightness() == 31
        assert color_temperature() == 30
        self.device.set_brightness_and_color_temperature(10, 11)
        assert brightness() == 10
        assert color_temperature() == 11

        with pytest.raises(CeilException):
            self.device.set_brightness_and_color_temperature(-1, 10)

        with pytest.raises(CeilException):
            self.device.set_brightness_and_color_temperature(10, -1)

        with pytest.raises(CeilException):
            self.device.set_brightness_and_color_temperature(0, 10)

        with pytest.raises(CeilException):
            self.device.set_brightness_and_color_temperature(10, 0)

        with pytest.raises(CeilException):
            self.device.set_brightness_and_color_temperature(101, 10)

        with pytest.raises(CeilException):
            self.device.set_brightness_and_color_temperature(10, 101)

    def test_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        self.device.delay_off(100)
        assert delay_off_countdown() == 100
        self.device.delay_off(200)
        assert delay_off_countdown() == 200

        with pytest.raises(CeilException):
            self.device.delay_off(0)

        with pytest.raises(CeilException):
            self.device.delay_off(-1)

    def test_set_scene(self):
        def scene():
            return self.device.status().scene

        self.device.set_scene(1)
        assert scene() == 1
        self.device.set_scene(4)
        assert scene() == 4

        with pytest.raises(CeilException):
            self.device.set_scene(0)

        with pytest.raises(CeilException):
            self.device.set_scene(5)

    def test_smart_night_light_on(self):
        def smart_night_light():
            return self.device.status().smart_night_light

        self.device.smart_night_light_off()
        assert smart_night_light() is False
        self.device.smart_night_light_on()
        assert smart_night_light() is True

    def test_automatic_color_temperature_on(self):
        def automatic_color_temperature():
            return self.device.status().automatic_color_temperature

        self.device.automatic_color_temperature_on()
        assert automatic_color_temperature() is True
        self.device.automatic_color_temperature_off()
        assert automatic_color_temperature() is False
