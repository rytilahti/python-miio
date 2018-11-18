from unittest import TestCase

import pytest

from miio import PhilipsMoonlight
from miio.philips_moonlight import PhilipsMoonlightStatus, PhilipsMoonlightException
from miio.utils import int_to_rgb
from .dummies import DummyDevice


class DummyPhilipsMoonlight(DummyDevice, PhilipsMoonlight):
    def __init__(self, *args, **kwargs):
        self.state = {
            'pow': 'on',
            'sta': 0,
            'bri': 1,
            'rgb': 16741971,
            'cct': 1,
            'snm': 0,
            'spr': 0,
            'spt': 15,
            'wke': 0,
            'bl': 1,
            'ms': 1,
            'mb': 1,
            'wkp': [0, 24, 0]
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("pow", x),
            'set_bright': lambda x: self._set_state("bri", x),
            'set_cct': lambda x: self._set_state("cct", x),
            'set_rgb': lambda x: self._set_state("rgb", x),
            'apply_fixed_scene': lambda x: self._set_state("snm", x),
            'set_bricct': lambda x: (
                self._set_state('bri', [x[0]]),
                self._set_state('cct', [x[1]])
            ),
            'set_brirgb': lambda x: (
                self._set_state('bri', [x[0]]),
                self._set_state('rgb', [x[1]])
            )
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def philips_moonlight(request):
    request.cls.device = DummyPhilipsMoonlight()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("philips_moonlight")
class TestPhilipsMoonlight(TestCase):
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

        assert repr(self.state()) == repr(PhilipsMoonlightStatus(self.device.start_state))

        assert self.is_on() is True
        assert self.state().brightness == self.device.start_state["bri"]
        assert self.state().color_temperature == self.device.start_state["cct"]
        assert self.state().rgb == int_to_rgb(int(self.device.start_state["rgb"]))
        assert self.state().scene == self.device.start_state["snm"]

    def test_set_brightness(self):
        def brightness():
            return self.device.status().brightness

        self.device.set_brightness(1)
        assert brightness() == 1
        self.device.set_brightness(50)
        assert brightness() == 50
        self.device.set_brightness(100)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness(-1)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness(0)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness(101)

    def test_set_rgb(self):
        def rgb():
            return self.device.status().rgb

        self.device.set_rgb((0, 0, 1))
        assert rgb() == (0, 0, 1)
        self.device.set_rgb((255, 255, 0))
        assert rgb() == (255, 255, 0)
        self.device.set_rgb((255, 255, 255))
        assert rgb() == (255, 255, 255)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_rgb((-1, 0, 0))

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_rgb((256, 0, 0))

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_rgb((0, -1, 0))

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_rgb((0, 256, 0))

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_rgb((0, 0, -1))

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_rgb((0, 0, 256))

    def test_set_color_temperature(self):
        def color_temperature():
            return self.device.status().color_temperature

        self.device.set_color_temperature(20)
        assert color_temperature() == 20
        self.device.set_color_temperature(30)
        assert color_temperature() == 30
        self.device.set_color_temperature(10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_color_temperature(-1)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_color_temperature(0)

        with pytest.raises(PhilipsMoonlightException):
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

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_color_temperature(-1, 10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_color_temperature(10, -1)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_color_temperature(0, 10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_color_temperature(10, 0)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_color_temperature(101, 10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_color_temperature(10, 101)

    def test_set_brightness_and_rgb(self):
        def brightness():
            return self.device.status().brightness

        def rgb():
            return self.device.status().rgb

        self.device.set_brightness_and_rgb(20, 0)
        assert brightness() == 20
        assert rgb() == (0, 0, 0)
        self.device.set_brightness_and_rgb(31, 16711680)
        assert brightness() == 31
        assert rgb() == (255, 0, 0)
        self.device.set_brightness_and_rgb(100, 16777215)
        assert brightness() == 100
        assert rgb() == (255, 255, 255)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_rgb(-1, 10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_rgb(10, -1)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_rgb(0, 10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_rgb(101, 10)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_brightness_and_rgb(10, 16777216)

    def test_set_scene(self):
        def scene():
            return self.device.status().scene

        self.device.set_scene(1)
        assert scene() == 1
        self.device.set_scene(2)
        assert scene() == 2

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_scene(-1)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_scene(0)

        with pytest.raises(PhilipsMoonlightException):
            self.device.set_scene(5)
