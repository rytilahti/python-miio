from unittest import TestCase
from miio import PhilipsBulb
from .dummies import DummyDevice
import pytest


class DummyPhilipsBulb(DummyDevice, PhilipsBulb):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'bright': 85,
            'cct': 9,
            'snm': 0,
            'dv': 0
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_bright': lambda x: self._set_state("bright", x),
            'set_cct': lambda x: self._set_state("cct", x),
            'delay_off': lambda x: self._set_state("dv", x),
            'apply_fixed_scene': lambda x: self._set_state("snm", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def philips_bulb(request):
    request.cls.device = DummyPhilipsBulb()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("philips_bulb")
class TestPhilipsBulb(TestCase):
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
        assert self.state().brightness == self.device.start_state["bright"]
        assert self.state().color_temperature == self.device.start_state["cct"]
        assert self.state().scene == self.device.start_state["snm"]
        assert self.state().delay_off_countdown == self.device.start_state["dv"]

    def test_set_brightness(self):
        def brightness():
            return self.device.status().brightness

        self.device.set_brightness(10)
        assert brightness() == 10
        self.device.set_brightness(20)
        assert brightness() == 20

    def test_set_color_temperature(self):
        def color_temperature():
            return self.device.status().color_temperature

        self.device.set_color_temperature(30)
        assert color_temperature() == 30
        self.device.set_color_temperature(20)
        assert color_temperature() == 20

    def test_delay_off(self):
        def delay_off_countdown():
            return self.device.status().delay_off_countdown

        self.device.delay_off(100)
        assert delay_off_countdown() == 100
        self.device.delay_off(200)
        assert delay_off_countdown() == 200

    def test_set_scene(self):
        def scene():
            return self.device.status().scene

        self.device.set_scene(1)
        assert scene() == 1
        self.device.set_scene(2)
        assert scene() == 2
