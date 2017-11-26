from unittest import TestCase
from miio import AirConditioningCompanion
from miio.airconditioningcompanion import OperationMode, FanSpeed
from .dummies import DummyDevice
import pytest


class DummyAirConditioningCompanion(AirConditioningCompanion):
    def __init__(self, *args, **kwargs):
        self.state = ['010500978022222102', '010201190280222221', '2']

        self.return_values = {
            'get_model_and_state': self._get_state
        }
        self.start_state = self.state.copy()

    def send(self, command: str, parameters=None, retry_count=3):
        """Overridden send() to return values from `self.return_values`."""
        return self.return_values[command](parameters)

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()

    def _get_state(self, props):
        """Return the requested data"""
        return self.state


@pytest.fixture(scope="class")
def airconditioningcompanion(request):
    request.cls.device = DummyAirConditioningCompanion()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("airconditioningcompanion")
class TestAirConditioningCompanion(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_status(self):
        self.device._reset_state()

        assert self.is_on() is False
        assert self.state().air_condition_power == '2'
        assert self.state().air_condition_model == '0180222221'
        assert self.state().temperature == 25
        assert self.state().swing_mode is False
        assert self.state().fan_speed == FanSpeed.Low
        assert self.state().mode == OperationMode.Auto
