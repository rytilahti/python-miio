from unittest import TestCase
from miio import PlugV1
import pytest


class DummyPlugV1(PlugV1):
    def __init__(self, *args, **kwargs):
        self.state = {
            'on': True,
            'usb_on': True,
            'temperature': 32,
        }
        self.return_values = {
            'get_prop': self._get_state,
            'set_on': lambda x: self._set_state("on", True),
            'set_off': lambda x: self._set_state("on", False),
            'set_usb_on': lambda x: self._set_state("usb_on", True),
            'set_usb_off': lambda x: self._set_state("usb_on", False),
        }
        self.start_state = self.state.copy()

    def send(self, command: str, parameters=None, retry_count=3):
        """Overridden send() to return values from `self.return_values`."""
        return self.return_values[command](parameters)

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()

    def _set_state(self, var, value):
        """Set a state of a variable"""
        self.state[var] = value

    def _get_state(self, props):
        """Return wanted properties"""
        return [self.state[x] for x in props if x in self.state]


@pytest.fixture(scope="class")
def plugv1(request):
    request.cls.device = DummyPlugV1()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("plugv1")
class TestPlugV1(TestCase):
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
        assert self.state().usb_power is True
        assert self.state().temperature == self.device.start_state[
            "temperature"]

    def test_usb_on(self):
        self.device.usb_off()  # ensure off
        assert self.device.status().usb_power is False

        self.device.usb_on()
        assert self.device.status().usb_power is True

    def test_usb_off(self):
        self.device.usb_on()  # ensure on
        assert self.device.status().usb_power is True

        self.device.usb_off()
        assert self.device.status().usb_power is False
