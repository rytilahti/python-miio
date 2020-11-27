from unittest import TestCase

import pytest

from miio import HuizuoMiot
from miio.huizuo import (
    HuizuoException,
)

from .dummies import DummyMiotDevice

_INITIAL_STATE = {
    "power": True,
    "brigtness": 60,
    "color_temp": 4000,
}


class DummyHuizuoMiot(DummyMiotDevice, HuizuoMiot):
    def __init__(self, *args, **kwargs):
        self.state = _INITIAL_STATE
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_brigtness": lambda x: self._set_state("brigtness", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="function")
def huizuo(request):
    request.cls.device = DummyHuizuoMiot()


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
        assert status.brigtness is _INITIAL_STATE["brigtness"]
        assert status.color_temp is _INITIAL_STATE["color_temp"]

    def test_brigtness(self):
        def lamp_brigtness():
            return self.device.status().brigtness

        self.device.set_brigtness(20)
        assert lamp_brigtness() == 20
        self.device.set_brigtness(80)
        assert lamp_brigtness() == 80

        with pytest.raises(HuizuoException):
            self.device.set_brigtness(-5)

        with pytest.raises(HuizuoException):
            self.device.set_brigtness(105)

    def test_color_temp(self):
        def lamp_color_temp():
            return self.device.status().color_temp

        self.device.set_color_temp(3500)
        assert lamp_color_temp() == 3500
        self.device.set_color_temp(5500)
        assert lamp_color_temp() == 5500

        with pytest.raises(HuizuoException):
            self.device.set_color_temp(2800)

        with pytest.raises(HuizuoException):
            self.device.set_color_temp(6500)
