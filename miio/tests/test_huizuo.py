from unittest import TestCase

import pytest

from miio import Huizuo
from miio.huizuo import HuizuoException

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": True,
    "brightness": 60,
    "color_temp": 4000,
}


class DummyHuizuo(DummyMiotDevice, Huizuo):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_brightness": lambda x: self._set_state("brightness", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def huizuo(request):
    request.cls.device = DummyHuizuo()


@pytest.mark.usefixtures("huizuo")
class TestHuizuo(TestCase):
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
        assert status.brightness is _INITIAL_STATE["brightness"]
        assert status.color_temp is _INITIAL_STATE["color_temp"]

    def test_brightness(self):
        def lamp_brightness():
            return self.device.status().brightness

        self.device.set_brightness(1)
        assert lamp_brightness() == 1
        self.device.set_brightness(64)
        assert lamp_brightness() == 64
        self.device.set_brightness(100)
        assert lamp_brightness() == 100

        with pytest.raises(HuizuoException):
            self.device.set_brightness(-1)

        with pytest.raises(HuizuoException):
            self.device.set_brightness(101)

    def test_color_temp(self):
        def lamp_color_temp():
            return self.device.status().color_temp

        self.device.set_color_temp(3000)
        assert lamp_color_temp() == 3000
        self.device.set_color_temp(4200)
        assert lamp_color_temp() == 4200
        self.device.set_color_temp(6400)
        assert lamp_color_temp() == 6400

        with pytest.raises(HuizuoException):
            self.device.set_color_temp(2999)

        with pytest.raises(HuizuoException):
            self.device.set_color_temp(6401)
