from unittest import TestCase
from miio import Plug
from .dummies import DummyDevice
import pytest

class DummyPlug(DummyDevice, Plug):
    def __init__(self, *args, **kwargs):
        self.state = {
            'power': 'on',
            'temperature': 32,
            'current': 123,
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_power': lambda x: self._set_state("power", x),
        }
        super().__init__(args, kwargs)

@pytest.fixture(scope="class")
def plug(request):
    request.cls.device = DummyPlug()
    # TODO add ability to test on a real device

@pytest.mark.usefixtures("plug")

class TestPlug(TestCase):
    def test_on(self):
        self.device.off()  # ensure off
        is_on = lambda: self.device.status().is_on
        start_state = is_on()
        assert start_state == False

        self.device.on()
        assert is_on() == True


    def test_off(self):
        self.device.on()  # ensure on
        is_on = lambda: self.device.status().is_on
        assert is_on() == True

        self.device.off()
        assert is_on() == False

    def test_status(self):
        self.device._reset_state()
        state = lambda: self.device.status()
        print(state())
        assert state().is_on == True
        assert state().temperature == self.device.start_state["temperature"]
        assert state().load_power ==  self.device.start_state["current"] * 110

    def test_status_without_current(self):
        del self.device.state["current"]
        state = lambda: self.device.status()
        assert state().load_power is None
