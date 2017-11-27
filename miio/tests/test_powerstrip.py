from unittest import TestCase
from miio import PowerStrip
from miio.powerstrip import PowerMode
from .dummies import DummyDevice
import pytest


class DummyPowerStrip(DummyDevice, PowerStrip):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'mode': 'normal',
            'temperature': 32.5,
            'current': 25.5,
            'power_consume_rate': 12.5,
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
            'set_power_mode': lambda x: self._set_state("mode", x),
        }
        super().__init__(args, kwargs)


@pytest.fixture(scope="class")
def powerstrip(request):
    request.cls.device = DummyPowerStrip()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("powerstrip")
class TestPowerStrip(TestCase):
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
        assert self.state().mode == PowerMode(self.device.start_state["mode"])
        assert self.state().temperature == self.device.start_state["temperature"]
        assert self.state().current == self.device.start_state["current"]
        assert self.state().load_power == self.device.start_state["power_consume_rate"]

    def test_status_without_power_consume_rate(self):
        del self.device.state["power_consume_rate"]

        assert self.state().load_power is None

    def test_set_power_mode(self):
        def mode():
            return self.device.status().mode

        self.device.set_power_mode(PowerMode.Eco)
        assert mode() == PowerMode.Eco
        self.device.set_power_mode(PowerMode.Normal)
        assert mode() == PowerMode.Normal
